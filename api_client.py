"""
API client for HighLevel integration and Meta Ads metrics
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
                'nonQualifie': non_qualifie,
                'sansReponse': sans_reponse
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
            inline_link_clicks = 0
            video_30_sec_watched = 0

            # Extract leads from conversions (priority)
            for conv in insights.get("conversions", []):
                if conv.get("action_type") == "schedule_total":
                    leads += int(conv.get("value", 0))

            # Extract from actions if no leads found in conversions
            for act in insights.get("actions", []):
                if act.get("action_type") == "lead" and leads == 0:
                    leads += int(act.get("value", 0))
                if act.get("action_type") == "inline_link_click":
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