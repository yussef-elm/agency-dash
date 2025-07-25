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

        # Count by canonical stage - INCLUDING non_qualifie and sans_reponse
        annule = confirme = pas_venu = present = concretise = non_confirme = non_qualifie = sans_reponse = 0
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
            elif o['stageCanonical'] == 'non_qualifie':
                non_qualifie += 1
            elif o['stageCanonical'] == 'sans_reponse':
                sans_reponse += 1

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
                'nonConfirme': non_confirme,
                'nonQualifie': non_qualifie,  # Added
                'sansReponse': sans_reponse   # Added
            }
        }

        # Stage stats - this will now include all canonical stages
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
        "fields": "ctr,cpm,spend,conversions,actions,video_30_sec_watched_actions,impressions,inline_link_clicks",
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
                    "impressions": 0,
                    "inline_link_clicks": 0,
                    "video_30_sec_watched": 0,
                    "hook_rate": 0.0,
                    "conversion_rate": 0.0,
                    "error": f"HTTP {response.status}: {response_text[:200]}"
                }

            data = await response.json()
            insights = data.get("data", [{}])[0] if data.get("data") else {}

            # Extract basic metrics
            leads = 0
            spend = float(insights.get("spend", 0))
            cpm = float(insights.get("cpm", 0))
            ctr = float(insights.get("ctr", 0))
            impressions = int(insights.get("impressions", 0))
            video_30_sec_watched = 0

            # Use inline_link_clicks field directly if present
            inline_link_clicks = int(insights.get("inline_link_clicks", 0))

            # Extract leads from conversions (priority)
            for conv in insights.get("conversions", []):
                if conv.get("action_type") == "schedule_total":
                    leads += int(conv.get("value", 0))

            # If inline_link_clicks is zero, fallback to summing 'link_click' from actions
            if inline_link_clicks == 0:
                for act in insights.get("actions", []):
                    if act.get("action_type") == "link_click":
                        inline_link_clicks += int(act.get("value", 0))

            # Extract 30s video views from video_30_sec_watched_actions if available
            if "video_30_sec_watched_actions" in insights:
                try:
                    for v in insights["video_30_sec_watched_actions"]:
                        video_30_sec_watched += int(v.get("value", 0))
                except Exception:
                    pass

            # Calculate CPR (Cost Per Result/Lead)
            cpr = spend / leads if leads > 0 else 0.0

            # Calculate hook rate (30s video views / impressions)
            hook_rate = (video_30_sec_watched / impressions * 100) if impressions > 0 else 0

            # Calculate conversion rate (leads / link clicks)
            conversion_rate = (leads / inline_link_clicks * 100) if inline_link_clicks > 0 else 0

            return {
                "leads": leads,
                "spend": spend,
                "cpm": cpm,
                "ctr": ctr,
                "cpr": cpr,
                "impressions": impressions,
                "inline_link_clicks": inline_link_clicks,
                "video_30_sec_watched": video_30_sec_watched,
                "hook_rate": hook_rate,
                "conversion_rate": conversion_rate
            }

    except Exception as e:
        return {
            "leads": 0,
            "spend": 0.0,
            "cpm": 0.0,
            "ctr": 0.0,
            "cpr": 0.0,
            "impressions": 0,
            "inline_link_clicks": 0,
            "video_30_sec_watched": 0,
            "hook_rate": 0.0,
            "conversion_rate": 0.0,
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
                    "impressions": 0,
                    "inline_link_clicks": 0,
                    "video_30_sec_watched": 0,
                    "hook_rate": 0.0,
                    "conversion_rate": 0.0,
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
                "impressions": 0,
                "inline_link_clicks": 0,
                "video_30_sec_watched": 0,
                "hook_rate": 0.0,
                "conversion_rate": 0.0,
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
    created_data = fetch_centers_data_created(start_date_str, end_date_str, selected_center_names)

    meta_data = fetch_meta_metrics_for_centers(start_date_str, end_date_str, selected_center_names, access_token)

    meta_data_dict = {m['centerName'].strip().lower(): m for m in meta_data}
    combined_results = []

    for created_center in created_data:
        center_name = created_center['centerName']
        center_key = center_name.strip().lower()
        meta_center = meta_data_dict.get(center_key, None)

        created_metrics = created_center.get('metrics', {})
        meta_metrics = meta_center['metrics'] if meta_center else {}

        # Convert to proper types
        spend = float(meta_metrics.get('spend', 0))
        meta_leads = int(meta_metrics.get('leads', 0))
        cpr = float(meta_metrics.get('cpr', 0))
        cpm = float(meta_metrics.get('cpm', 0))
        ctr = float(meta_metrics.get('ctr', 0))
        impressions = int(meta_metrics.get('impressions', 0))
        inline_link_clicks = int(meta_metrics.get('inline_link_clicks', 0))
        video_30_sec_watched = int(meta_metrics.get('video_30_sec_watched', 0))
        hook_rate = float(meta_metrics.get('hook_rate', 0))
        meta_conversion_rate = float(meta_metrics.get('conversion_rate', 0))

        concretise = int(created_metrics.get('details', {}).get('concretise', 0))
        total_created = int(created_metrics.get('totalRDVPlanifies', 0))
        confirmation_rate = float(created_metrics.get('confirmationRateNum', 0))
        conversion_rate = float(created_metrics.get('conversionRateNum', 0))
        cancellation_rate = float(created_metrics.get('cancellationRateNum', 0))
        no_show_rate = float(created_metrics.get('noShowRateNum', 0))

        cpa = round(spend / concretise, 2) if concretise > 0 else 0
        cpl = round(spend / meta_leads, 2) if meta_leads > 0 else 0
        lead_to_sale_rate = round((concretise / meta_leads * 100), 2) if meta_leads > 0 else 0
        lead_to_appointment_rate = round((total_created / meta_leads * 100), 2) if meta_leads > 0 else 0

        combined_results.append({
            'centerName': center_name,
            'city': created_center['city'],
            'meta_leads': meta_leads,
            'spend': spend,
            'cpm': cpm,
            'ctr': ctr,
            'cpr': cpr,
            'impressions': impressions,
            'inline_link_clicks': inline_link_clicks,
            'video_30_sec_watched': video_30_sec_watched,
            'hook_rate': hook_rate,
            'meta_conversion_rate': meta_conversion_rate,
            'total_created': total_created,
            'concretise': concretise,
            'confirmation_rate': confirmation_rate,
            'conversion_rate': conversion_rate,
            'cancellation_rate': cancellation_rate,
            'no_show_rate': no_show_rate,
            'cpa': cpa,
            'cpl': cpl,
            'lead_to_sale_rate': lead_to_sale_rate,
            'lead_to_appointment_rate': lead_to_appointment_rate,
            'has_meta_error': 'error' in meta_metrics,
            'has_created_error': 'error' in created_center,
            'meta_error': meta_metrics.get('error', ''),
            'created_error': created_center.get('error', '')
        })

    return combined_results
def format_combined_data_for_display(combined_data):
    """Format combined data for display in Streamlit tables - returns raw numbers, no string formatting"""
    display_data = []

    def safe_float(val, default=0.0):
        try:
            return float(val)
        except (TypeError, ValueError):
            return default

    def safe_int(val, default=0):
        try:
            return int(val)
        except (TypeError, ValueError):
            return default

    for center in combined_data:

        formatted = {
            'Centre': center.get('centerName', ''),
            'Ville': center.get('city', ''),
            'Impressions': safe_int(center.get('impressions')),
            'Clics': safe_int(center.get('inline_link_clicks')),
            'Leads Meta': safe_int(center.get('meta_leads')),
            'Vues 30s': safe_int(center.get('video_30_sec_watched')),
            'Hook Rate (%)': safe_float(center.get('hook_rate')),
            'Meta Conv. Rate (%)': safe_float(center.get('meta_conversion_rate')),
            'CPR (€)': safe_float(center.get('cpr')),
            'CPM (€)': safe_float(center.get('cpm')),
            'CTR (%)': safe_float(center.get('ctr')),
            'Dépense (€)': safe_float(center.get('spend')),
            'Nb RDV': safe_int(center.get('total_created')),
            'Concrétisé': safe_int(center.get('concretise')),
            'Taux Confirmation (%)': safe_float(center.get('confirmation_rate')),
            'Taux Conversion (%)': safe_float(center.get('conversion_rate')),
            'Taux Annulation (%)': safe_float(center.get('cancellation_rate')),
            'Taux No-Show (%)': safe_float(center.get('no_show_rate')),
            'CPL (€)': safe_float(center.get('cpl')),
            'CPA - Coût/Concrétisation (€)': safe_float(center.get('cpa')),
            'Lead→RDV (%)': safe_float(center.get('lead_to_appointment_rate')),
            'Lead→Sale (%)': safe_float(center.get('lead_to_sale_rate'))
        }

        print(f"  Formatted data (raw): {formatted}")
        display_data.append(formatted)

    return display_data


def get_performance_summary(combined_data):
    """Get summary statistics for all centers"""
    if not combined_data:
        print("[DEBUG] No combined data provided.")
        return {}

    valid_centers = [c for c in combined_data if not c.get('has_meta_error') and not c.get('has_created_error')]

    if not valid_centers:
        print("[DEBUG] No valid centers after filtering errors.")
        return {'error': 'No valid data available'}

    def safe_float(val, default=0.0):
        try:
            return float(val)
        except (TypeError, ValueError):
            return default

    def safe_sum(key):
        s = sum(safe_float(c.get(key, 0)) for c in valid_centers)
        return s

    total_spend = safe_sum('spend')
    total_meta_leads = safe_sum('meta_leads')
    total_created = safe_sum('total_created')
    total_concretise = safe_sum('concretise')
    total_impressions = safe_sum('impressions')
    total_clicks = safe_sum('inline_link_clicks')
    total_video_30s = safe_sum('video_30_sec_watched')

    total_cpm = sum(safe_float(c.get('cpm', 0)) * safe_float(c.get('spend', 0)) for c in valid_centers if safe_float(c.get('spend', 0)) > 0)
    total_ctr = sum(safe_float(c.get('ctr', 0)) * safe_float(c.get('spend', 0)) for c in valid_centers if safe_float(c.get('spend', 0)) > 0)
    total_cpr = sum(safe_float(c.get('cpr', 0)) * safe_float(c.get('spend', 0)) for c in valid_centers if safe_float(c.get('spend', 0)) > 0)

    weighted_cpm = (total_cpm / total_spend) if total_spend > 0 else 0
    weighted_ctr = (total_ctr / total_spend) if total_spend > 0 else 0
    weighted_cpr = (total_cpr / total_spend) if total_spend > 0 else 0


    n = len(valid_centers)
    avg_confirmation_rate = round(sum(safe_float(c.get('confirmation_rate')) for c in valid_centers) / n, 2) if n else 0
    avg_cancellation_rate = round(sum(safe_float(c.get('cancellation_rate')) for c in valid_centers) / n, 2) if n else 0
    avg_no_show_rate = round(sum(safe_float(c.get('no_show_rate')) for c in valid_centers) / n, 2) if n else 0


    summary = {
        'total_centers': n,
        'total_spend': total_spend,
        'total_impressions': total_impressions,
        'total_clicks': total_clicks,
        'total_video_30s': total_video_30s,
        'total_meta_leads': total_meta_leads,
        'total_created': total_created,
        'total_concretise': total_concretise,
        'avg_cpa': round(total_spend / total_concretise, 2) if total_concretise > 0 else 0,
        'avg_cpl': round(total_spend / total_meta_leads, 2) if total_meta_leads > 0 else 0,
        'avg_cpm': round(weighted_cpm, 2),
        'avg_ctr': round(weighted_ctr, 2),
        'avg_cpr': round(weighted_cpr, 2),
        'overall_hook_rate': round((total_video_30s / total_impressions * 100), 2) if total_impressions > 0 else 0,
        'overall_meta_conversion_rate': round((total_meta_leads / total_clicks * 100), 2) if total_clicks > 0 else 0,
        'overall_lead_to_appointment': round((total_created / total_meta_leads * 100), 2) if total_meta_leads > 0 else 0,
        'overall_lead_to_sale': round((total_concretise / total_meta_leads * 100), 2) if total_meta_leads > 0 else 0,
        'overall_conversion_rate': round((total_concretise / total_created * 100), 2) if total_created > 0 else 0,
        'overall_confirmation_rate': avg_confirmation_rate,
        'overall_cancellation_rate': avg_cancellation_rate,
        'overall_no_show_rate': avg_no_show_rate
    }

    return summary