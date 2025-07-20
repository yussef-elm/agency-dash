"""
API client for HighLevel integration
"""
import asyncio
import aiohttp
import streamlit as st
from datetime import datetime, timezone, time
from utils import canonical, pct, pct_str, EXCLUDED_STAGE_CANON

async def fetch_all_opportunities(session, url_base, center):
    """Fetch all opportunities with pagination"""
    items = []
    start_after_id = None
    start_after = None
    has_more = True

    while has_more:
        url = f"{url_base}?limit=100"
        if start_after_id and start_after:
            url += f"&startAfterId={start_after_id}&startAfter={start_after}"

        headers = {
            'Authorization': f'Bearer {center["apiKey"]}',
            'Location-Id': center["locationId"]
        }

        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    break
                data = await response.json()
                items.extend(data.get('opportunities', []))

                meta = data.get('meta', {})
                if meta.get('nextPageUrl'):
                    start_after_id = meta.get('startAfterId')
                    start_after = meta.get('startAfter')
                else:
                    has_more = False
        except Exception as e:
            st.error(f"Error fetching data for {center['centerName']}: {str(e)}")
            break

    return items

async def get_center_stats_base(session, center, start_datetime, end_datetime, date_field='updatedAt'):
    """Base function for getting center stats with configurable date field"""
    try:
        # Fetch pipelines
        pipeline_url = 'https://rest.gohighlevel.com/v1/pipelines/'
        headers = {
            'Authorization': f'Bearer {center["apiKey"]}',
            'Location-Id': center["locationId"]
        }

        async with session.get(pipeline_url, headers=headers) as response:
            if response.status != 200:
                return {
                    'centerName': center['centerName'],
                    'city': center['city'],
                    'error': f'Failed to fetch pipelines: {response.status}'
                }

            data = await response.json()
            pipelines = data.get('pipelines', [])

        # Find target pipeline
        target_pipeline = next((p for p in pipelines if p['name'] == center['pipelineName']), None)
        if not target_pipeline:
            return {
                'centerName': center['centerName'],
                'city': center['city'],
                'error': 'Pipeline not found'
            }

        # Create stage mapping
        stage_id_to_name = {stage['id']: stage['name'] for stage in target_pipeline.get('stages', [])}

        # Fetch opportunities
        opp_url = f"https://rest.gohighlevel.com/v1/pipelines/{target_pipeline['id']}/opportunities"
        all_opportunities = await fetch_all_opportunities(session, opp_url, center)

        # Filter by date (using specified date field)
        opp_filtered_by_date = [
            {
                **opp,
                'stageName': stage_id_to_name.get(opp.get('pipelineStageId', ''), ''),
                'stageCanonical': canonical(stage_id_to_name.get(opp.get('pipelineStageId', ''), ''))
            }
            for opp in all_opportunities
            if opp.get(date_field) and start_datetime <= datetime.fromisoformat(opp[date_field].replace('Z', '+00:00')) <= end_datetime
        ]

        # TOTAL = All opportunities in pipeline (excluding Database Reactivation)
        totalRDVPlanifies = sum(1 for o in opp_filtered_by_date if o['stageCanonical'] != EXCLUDED_STAGE_CANON)

        # Filter out Database Reactivation for stage counting
        opp_filtered = [o for o in opp_filtered_by_date if o['stageCanonical'] != EXCLUDED_STAGE_CANON]

        # Count by canonical stage
        annule = confirme = pas_venu = present = concretise = non_confirme = 0
        for o in opp_filtered:
            if o['stageCanonical'] == 'annule':
                annule += 1
            elif o['stageCanonical'] == 'confirme':
                confirme += 1
            elif o['stageCanonical'] == 'pas_venu':
                pas_venu += 1
            elif o['stageCanonical'] == 'present':
                present += 1
            elif o['stageCanonical'] == 'concretise':
                concretise += 1
            elif o['stageCanonical'] == 'non_confirme':
                non_confirme += 1

        confirmes = confirme + pas_venu + present + concretise
        show_up = present + concretise

        # Calculate metrics with numeric values for color coding
        confirmation_rate = pct(confirmes, totalRDVPlanifies)
        cancellation_rate = pct(annule, totalRDVPlanifies)
        no_show_rate = pct(pas_venu, confirmes)
        presence_rate = pct(show_up, confirmes)
        conversion_rate = pct(concretise, show_up)

        metrics = {
            'totalRDVPlanifies': totalRDVPlanifies,
            'rdvConfirmes': confirmes,
            'showUp': show_up,
            'tauxConfirmation': pct_str(confirmes, totalRDVPlanifies),
            'tauxAnnulation': pct_str(annule, totalRDVPlanifies),
            'tauxNoShow': pct_str(pas_venu, confirmes),
            'tauxPresence': pct_str(show_up, confirmes),
            'tauxConversion': pct_str(concretise, show_up),
            # Numeric values for color coding
            'confirmationRateNum': confirmation_rate,
            'cancellationRateNum': cancellation_rate,
            'noShowRateNum': no_show_rate,
            'presenceRateNum': presence_rate,
            'conversionRateNum': conversion_rate,
            'details': {
                'annule': annule,
                'confirme': confirme,
                'pasVenu': pas_venu,
                'present': present,
                'concretise': concretise,
                'nonConfirme': non_confirme
            }
        }

        # Stage stats
        stageStats = {}
        for o in opp_filtered:
            stageCanonical = o['stageCanonical'] or 'unknown'
            stageStats[stageCanonical] = stageStats.get(stageCanonical, 0) + 1

        return {
            'centerName': center['centerName'],
            'city': center['city'],
            'pipeline': {'id': target_pipeline['id'], 'name': target_pipeline['name']},
            'stageStats': stageStats,
            'metrics': metrics,
            'filter': {
                'startDate': start_datetime.isoformat(),
                'endDate': end_datetime.isoformat()
            }
        }

    except Exception as e:
        return {
            'centerName': center['centerName'],
            'city': center['city'],
            'error': str(e)
        }

async def get_center_stats(session, center, start_datetime, end_datetime):
    """Get statistics for a single center (filtered by updatedAt)"""
    return await get_center_stats_base(session, center, start_datetime, end_datetime, 'updatedAt')

async def get_center_stats_created(session, center, start_datetime, end_datetime):
    """Get statistics for a single center (filtered by createdAt)"""
    return await get_center_stats_base(session, center, start_datetime, end_datetime, 'createdAt')

def _prepare_datetime_range(start_date_str, end_date_str):
    """Helper function to prepare datetime range"""
    start_date = datetime.fromisoformat(start_date_str)
    end_date = datetime.fromisoformat(end_date_str)
    start_datetime = datetime.combine(start_date.date(), time.min).replace(tzinfo=timezone.utc)
    end_datetime = datetime.combine(end_date.date(), time.max).replace(tzinfo=timezone.utc)
    return start_datetime, end_datetime

def _execute_async_tasks(tasks):
    """Helper function to execute async tasks"""
    async def fetch_all():
        async with aiohttp.ClientSession() as session:
            return await asyncio.gather(*tasks(session))

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(fetch_all())

@st.cache_data(ttl=300)
def fetch_centers_data(start_date_str, end_date_str, selected_center_names):
    """Fetch data for selected centers (filtered by updatedAt)"""
    from config import CENTERS
    
    start_datetime, end_datetime = _prepare_datetime_range(start_date_str, end_date_str)
    selected_centers = [c for c in CENTERS if c['centerName'] in selected_center_names]

    def create_tasks(session):
        return [get_center_stats(session, center, start_datetime, end_datetime) for center in selected_centers]

    return _execute_async_tasks(create_tasks)

@st.cache_data(ttl=300)
def fetch_centers_data_created(start_date_str, end_date_str, selected_center_names):
    """Fetch data for selected centers (filtered by createdAt)"""
    from config import CENTERS
    
    start_datetime, end_datetime = _prepare_datetime_range(start_date_str, end_date_str)
    selected_centers = [c for c in CENTERS if c['centerName'] in selected_center_names]

    def create_tasks(session):
        return [get_center_stats_created(session, center, start_datetime, end_datetime) for center in selected_centers]

    return _execute_async_tasks(create_tasks)

# APPOINTMENTS FUNCTIONS
async def fetch_appointments_from_calendar(session, center, calendar_id, start_date, end_date):
    """Fetch appointments from a single calendar within date range"""
    try:
        start_epoch = int(datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc).timestamp() * 1000)
        end_epoch = int(datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc).timestamp() * 1000)

        url = f"https://rest.gohighlevel.com/v1/appointments/?startDate={start_epoch}&endDate={end_epoch}&calendarId={calendar_id}&includeAll=true"

        headers = {
            'Authorization': f'Bearer {center["apiKey"]}',
            'Location-Id': center["locationId"]
        }

        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                return []
            data = await response.json()
            return data.get('appointments', [])
    except Exception as e:
        return []

def get_date_from_iso(iso_string):
    return iso_string.split('T')[0] if iso_string else 'unknown'

def merge_appointments_by_day(appointments):
    appointments_by_day = {}
    for appointment in appointments:
        date = get_date_from_iso(appointment.get('startTime'))
        status = appointment.get('appointmentStatus') or appointment.get('status') or 'unknown'
        status = status.lower()

        if date not in appointments_by_day:
            appointments_by_day[date] = {'total': 0}
        appointments_by_day[date]['total'] += 1
        appointments_by_day[date][status] = appointments_by_day[date].get(status, 0) + 1
    return appointments_by_day

async def fetch_appointments(session, center, start_date, end_date):
    """Fetch appointments from one or two calendars for a center"""
    all_appointments = []

    # Fetch from primary calendar
    appointments1 = await fetch_appointments_from_calendar(session, center, center.get('calendarId'), start_date, end_date)
    all_appointments.extend(appointments1)

    # Fetch from secondary calendar if exists
    if center.get('calendarId2'):
        appointments2 = await fetch_appointments_from_calendar(session, center, center.get('calendarId2'), start_date, end_date)
        all_appointments.extend(appointments2)

    appointments_by_day = merge_appointments_by_day(all_appointments)

    return {
        'centerName': center['centerName'],
        'city': center['city'],
        'locationId': center['locationId'],
        'calendarId': center.get('calendarId'),
        'calendarId2': center.get('calendarId2'),
        'appointmentsByDay': appointments_by_day,
        'totalAppointments': len(all_appointments)
    }

@st.cache_data(ttl=300)
def fetch_appointments_for_centers(start_date_str, end_date_str, selected_center_names):
    from config import CENTERS
    
    selected_centers = [c for c in CENTERS if c['centerName'] in selected_center_names]

    def create_tasks(session):
        return [fetch_appointments(session, center, start_date_str, end_date_str) for center in selected_centers]

    results = _execute_async_tasks(create_tasks)

    # --- CUMULATIVE CALCULATION ---
    for center in results:
        appointments_by_day = center.get('appointmentsByDay', {})
        totals = {}
        total_appointments = 0
        
        for day_data in appointments_by_day.values():
            total_appointments += day_data.get('total', 0)
            for status, count in day_data.items():
                if status != 'total':
                    totals[status] = totals.get(status, 0) + count
        
        center['totals'] = totals
        center['totalAppointments'] = total_appointments
        
        # Calculate ratios with your formulas
        confirmed = totals.get('confirmed', 0)
        cancelled = totals.get('cancelled', 0)
        noshow = totals.get('noshow', 0)
        showed = totals.get('showed', 0)
        
        if total_appointments > 0:
            # confirmationRate = (confirmed + showed + noshow) / total
            confirmed_total = confirmed + showed + noshow
            confirmation_rate = confirmed_total / total_appointments * 100
            
            # cancellationRate = cancelled / total
            cancellation_rate = cancelled / total_appointments * 100
            
            # noShowRate = noshow / confirmed (if confirmed > 0, else 0)
            no_show_rate = (noshow / confirmed_total * 100) if confirmed_total > 0 else 0
            
            # showUpRate = showed / confirmed (if confirmed > 0, else 0)
            show_up_rate = (showed / confirmed_total * 100) if confirmed_total > 0 else 0
            
            center['ratios'] = {
                'confirmationRate': round(confirmation_rate, 2),
                'cancellationRate': round(cancellation_rate, 2),
                'noShowRate': round(no_show_rate, 2),
                'showUpRate': round(show_up_rate, 2)
            }
        else:
            center['ratios'] = {
                'confirmationRate': 0.0,
                'cancellationRate': 0.0,
                'noShowRate': 0.0,
                'showUpRate': 0.0
            }
    
    return results

# META ADS FUNCTIONS
async def fetch_meta_metrics(session, business_id, access_token, date_start, date_stop):
    """Fetch Meta Ads metrics for a business account"""
    url = f"https://graph.facebook.com/v21.0/{business_id}/insights"
    
    params = {
        "fields": "ctr,cpm,spend,conversions,actions",
        "time_range": f"{{'since':'{date_start}','until':'{date_stop}'}}",
        "access_token": access_token
    }
    
    try:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                response_text = await response.text()
                return {
                    "leads": 0,
                    "spend": 0.0,
                    "cpm": 0.0,
                    "ctr": 0.0,
                    "cpr": 0.0,
                    "error": f"HTTP {response.status}: {response_text[:200]}"
                }
            
            data = await response.json()
            insights = data.get("data", [{}])[0] if data.get("data") else {}
            
            # Extract basic metrics
            leads = 0
            spend = float(insights.get("spend", 0))
            cpm = float(insights.get("cpm", 0))
            ctr = float(insights.get("ctr", 0))
            
            # Extract leads from conversions (priority)
            for conv in insights.get("conversions", []):
                if conv.get("action_type") == "schedule_total":
                    leads += int(conv.get("value", 0))
            
            # If no leads found in conversions, try actions
            if leads == 0:
                for act in insights.get("actions", []):
                    if act.get("action_type") == "lead":
                        leads += int(act.get("value", 0))
            
            # Calculate CPR (Cost Per Result/Lead)
            cpr = spend / leads if leads > 0 else 0.0
            
            return {
                "leads": leads,
                "spend": spend,
                "cpm": cpm,
                "ctr": ctr,
                "cpr": cpr
            }
            
    except Exception as e:
        return {
            "leads": 0,
            "spend": 0.0,
            "cpm": 0.0,
            "ctr": 0.0,
            "cpr": 0.0,
            "error": str(e)
        }

async def get_center_meta_stats(session, center, access_token, start_date_str, end_date_str):
    """Get Meta Ads statistics for a single center"""
    try:
        # Skip centers without businessId
        if not center.get('businessId') or center.get('businessId') == 'None':
            return {
                'centerName': center['centerName'],
                'city': center['city'],
                'businessId': None,
                'metrics': {
                    "leads": 0,
                    "spend": 0.0,
                    "cpm": 0.0,
                    "ctr": 0.0,
                    "cpr": 0.0,
                    "error": "No business ID configured"
                }
            }
        
        # Fetch Meta metrics
        metrics = await fetch_meta_metrics(
            session, 
            center['businessId'], 
            access_token, 
            start_date_str, 
            end_date_str
        )
        
        return {
            'centerName': center['centerName'],
            'city': center['city'],
            'businessId': center['businessId'],
            'metrics': metrics
        }
        
    except Exception as e:
        return {
            'centerName': center['centerName'],
            'city': center['city'],
            'businessId': center.get('businessId'),
            'metrics': {
                "leads": 0,
                "spend": 0.0,
                "cpm": 0.0,
                "ctr": 0.0,
                "cpr": 0.0,
                "error": str(e)
            }
        }

@st.cache_data(ttl=300)
def fetch_meta_metrics_for_centers(start_date_str, end_date_str, selected_center_names, access_token):
    """Fetch Meta Ads metrics for selected centers"""
    from config import CENTERS
    
    selected_centers = [c for c in CENTERS if c['centerName'] in selected_center_names]
    
    def create_tasks(session):
        return [
            get_center_meta_stats(session, center, access_token, start_date_str, end_date_str) 
            for center in selected_centers
        ]
    
    return _execute_async_tasks(create_tasks)

@st.cache_data(ttl=300)
def fetch_combined_performance_data(start_date_str, end_date_str, selected_center_names, access_token):
    """Fetch combined data: HighLevel created leads + Meta Ads metrics for CPA calculation"""
    # Get created leads data (for conversion rates)
    created_data = fetch_centers_data_created(start_date_str, end_date_str, selected_center_names)
    
    # Get Meta Ads data
    meta_data = fetch_meta_metrics_for_centers(start_date_str, end_date_str, selected_center_names, access_token)
    
    # Combine the data
    combined_results = []
    
    for created_center in created_data:
        center_name = created_center['centerName']
        
        # Find matching Meta data
        meta_center = next((m for m in meta_data if m['centerName'] == center_name), None)
        
        # Extract metrics
        created_metrics = created_center.get('metrics', {})
        meta_metrics = meta_center['metrics'] if meta_center else {}
        
        # Get key values
        spend = meta_metrics.get('spend', 0)
        meta_leads = meta_metrics.get('leads', 0)
        cpr = meta_metrics.get('cpr', 0)
        cpm = meta_metrics.get('cpm', 0)
        ctr = meta_metrics.get('ctr', 0)
        
        # HighLevel metrics
        concretise = created_metrics.get('details', {}).get('concretise', 0)
        total_created = created_metrics.get('totalRDVPlanifies', 0)
        confirmation_rate = created_metrics.get('confirmationRateNum', 0)
        conversion_rate = created_metrics.get('conversionRateNum', 0)
        cancellation_rate = created_metrics.get('cancellationRateNum', 0)
        no_show_rate = created_metrics.get('noShowRateNum', 0)
        
        # Calculate Cost Per Acquisition (CPA) = spend / concretise (cost per concrétisation)
        cpa = round(spend / concretise, 2) if concretise > 0 else 0
        
        # Calculate Cost Per Lead (CPL) = spend / meta_leads
        cpl = round(spend / meta_leads, 2) if meta_leads > 0 else 0
        
        # Calculate Lead to Sale Conversion Rate = concretise / meta_leads
        lead_to_sale_rate = round((concretise / meta_leads * 100), 2) if meta_leads > 0 else 0
        
        # Calculate Lead to Appointment Rate = total_created / meta_leads
        lead_to_appointment_rate = round((total_created / meta_leads * 100), 2) if meta_leads > 0 else 0
        
        combined_results.append({
            'centerName': center_name,
            'city': created_center['city'],
            # Meta metrics
            'meta_leads': meta_leads,
            'spend': spend,
            'cpm': cpm,
            'ctr': ctr,
            'cpr': cpr,
            # HighLevel metrics
            'total_created': total_created,
            'concretise': concretise,
            'confirmation_rate': confirmation_rate,
            'conversion_rate': conversion_rate,
            'cancellation_rate': cancellation_rate,
            'no_show_rate': no_show_rate,
            # Combined calculations
            'cpa': cpa,  # Cost Per Acquisition (cost per concrétisation)
            'cpl': cpl,  # Cost Per Lead
            'lead_to_sale_rate': lead_to_sale_rate,  # Lead to Sale %
            'lead_to_appointment_rate': lead_to_appointment_rate,  # Lead to Appointment %
            # Error flags
            'has_meta_error': 'error' in meta_metrics,
            'has_created_error': 'error' in created_center,
            'meta_error': meta_metrics.get('error', ''),
            'created_error': created_center.get('error', '')
        })
    
    return combined_results

def format_combined_data_for_display(combined_data):
    """Format combined data for display in Streamlit tables"""
    display_data = []
    
    for center in combined_data:
        display_data.append({
            'Centre': center['centerName'],
            'Ville': center['city'],
            # Meta Ads metrics
            'CPR (€)': f"{center['cpr']:.2f}",
            'CPM (€)': f"{center['cpm']:.2f}",
            'CTR (%)': f"{center['ctr']:.2f}%",
            'Dépense (€)': f"{center['spend']:.2f}",
            # HighLevel metrics
            'Nb RDV': center['total_created'],
            'Concrétisé': center['concretise'],
            # Ratios
            'Taux Confirmation (%)': f"{center['confirmation_rate']:.1f}%",
            'Taux Conversion (%)': f"{center['conversion_rate']:.1f}%",
            'Taux Annulation (%)': f"{center['cancellation_rate']:.1f}%",
            'Taux No-Show (%)': f"{center['no_show_rate']:.1f}%",
            # Cost per acquisition (cost per concrétisation)
            'CPA - Coût/Concrétisation (€)': f"{center['cpa']:.2f}"
        })
    
    return display_data

def get_performance_summary(combined_data):
    """Get summary statistics for all centers"""
    if not combined_data:
        return {}
    
    # Filter out centers with errors
    valid_centers = [c for c in combined_data if not c['has_meta_error'] and not c['has_created_error']]
    
    if not valid_centers:
        return {'error': 'No valid data available'}
    
    total_spend = sum(c['spend'] for c in valid_centers)
    total_meta_leads = sum(c['meta_leads'] for c in valid_centers)
    total_created = sum(c['total_created'] for c in valid_centers)
    total_concretise = sum(c['concretise'] for c in valid_centers)
    
    # Calculate weighted averages for rates
    total_cpm = sum(c['cpm'] * c['spend'] for c in valid_centers if c['spend'] > 0)
    total_ctr = sum(c['ctr'] * c['spend'] for c in valid_centers if c['spend'] > 0)
    total_cpr = sum(c['cpr'] * c['spend'] for c in valid_centers if c['spend'] > 0)
    
    weighted_cpm = (total_cpm / total_spend) if total_spend > 0 else 0
    weighted_ctr = (total_ctr / total_spend) if total_spend > 0 else 0
    weighted_cpr = (total_cpr / total_spend) if total_spend > 0 else 0
    
    return {
        'total_centers': len(valid_centers),
        'total_spend': total_spend,
        'total_meta_leads': total_meta_leads,
        'total_created': total_created,
        'total_concretise': total_concretise,
        'avg_cpa': round(total_spend / total_concretise, 2) if total_concretise > 0 else 0,
        'avg_cpl': round(total_spend / total_meta_leads, 2) if total_meta_leads > 0 else 0,
        'avg_cpm': round(weighted_cpm, 2),
        'avg_ctr': round(weighted_ctr, 2),
        'avg_cpr': round(weighted_cpr, 2),
        'overall_lead_to_appointment': round((total_created / total_meta_leads * 100), 2) if total_meta_leads > 0 else 0,
        'overall_lead_to_sale': round((total_concretise / total_meta_leads * 100), 2) if total_meta_leads > 0 else 0,
        'overall_conversion_rate': round((total_concretise / total_created * 100), 2) if total_created > 0 else 0,
        'overall_confirmation_rate': round(sum(c['confirmation_rate'] for c in valid_centers) / len(valid_centers), 2) if valid_centers else 0,
        'overall_cancellation_rate': round(sum(c['cancellation_rate'] for c in valid_centers) / len(valid_centers), 2) if valid_centers else 0,
        'overall_no_show_rate': round(sum(c['no_show_rate'] for c in valid_centers) / len(valid_centers), 2) if valid_centers else 0
    }
    """Get summary statistics for all centers"""
    if not combined_data:
        return {}
    
    # Filter out centers with errors
    valid_centers = [c for c in combined_data if not c['has_meta_error'] and not c['has_created_error']]
    
    if not valid_centers:
        return {'error': 'No valid data available'}
    
    total_spend = sum(c['spend'] for c in valid_centers)
    total_meta_leads = sum(c['meta_leads'] for c in valid_centers)
    total_created = sum(c['total_created'] for c in valid_centers)
    total_concretise = sum(c['concretise'] for c in valid_centers)
    
    return {
        'total_centers': len(valid_centers),
        'total_spend': total_spend,
        'total_meta_leads': total_meta_leads,
        'total_created': total_created,
        'total_concretise': total_concretise,
        'avg_cpa': round(total_spend / total_concretise, 2) if total_concretise > 0 else 0,
        'avg_cpl': round(total_spend / total_meta_leads, 2) if total_meta_leads > 0 else 0,
        'overall_lead_to_appointment': round((total_created / total_meta_leads * 100), 2) if total_meta_leads > 0 else 0,
        'overall_lead_to_sale': round((total_concretise / total_meta_leads * 100), 2) if total_meta_leads > 0 else 0,
        'overall_conversion_rate': round((total_concretise / total_created * 100), 2) if total_created > 0 else 0
    }