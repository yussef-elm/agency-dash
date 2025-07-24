"""
Enhanced UI components for the dashboard including colored tables with Meta Ads metrics
"""
import streamlit as st
import pandas as pd
from utils import get_color_class, create_metric_card

def create_colored_dataframe(df, metric_columns):
    """Create a dataframe with colored cells based on performance"""

    def color_cells(val, column_name):
        """Apply color styling to cells"""
        if column_name in metric_columns:
            metric_type = metric_columns[column_name]
            color_class = get_color_class(val, metric_type)

            if color_class == 'cell-green':
                return 'background-color: #d4edda; color: #155724; font-weight: bold'
            elif color_class == 'cell-yellow':
                return 'background-color: #fff3cd; color: #856404; font-weight: bold'
            elif color_class == 'cell-red':
                return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
            else:
                return 'background-color: #f8f9fa; color: #495057'
        return ''

    styled_df = df.style

    for col in df.columns:
        if col in metric_columns:
            styled_df = styled_df.applymap(
                lambda x: color_cells(x, col), 
                subset=[col]
            )

    return styled_df

def display_enhanced_benchmark_legend():
    """Enhanced benchmark legend including Meta Ads metrics"""
    st.markdown("""
    <div style="
        background: linear-gradient(90deg, #f8f9fa, #e9ecef);
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 12px 0;
        font-size: 13px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <div style="font-weight: 600; color: #2c3e50; margin-bottom: 8px;">📊 Performance Benchmarks</div>

        <div style="display: flex; flex-wrap: wrap; gap: 16px;">
            <div style="color: #636e72;">
                <strong>HighLevel:</strong>
                Confirmation: <span style="color: #00b894;">🟢>60%</span> <span style="color: #fdcb6e;">🟡40-60%</span> <span style="color: #e17055;">🔴<40%</span>
            </div>
            <div style="color: #636e72;">
                Show Up: <span style="color: #00b894;">🟢>50%</span> <span style="color: #fdcb6e;">🟡35-50%</span> <span style="color: #e17055;">🔴<35%</span>
            </div>
            <div style="color: #636e72;">
                Conversion: <span style="color: #00b894;">🟢>50%</span> <span style="color: #fdcb6e;">🟡30-50%</span> <span style="color: #e17055;">🔴<30%</span>
            </div>
        </div>

        <div style="display: flex; flex-wrap: wrap; gap: 16px; margin-top: 8px;">
            <div style="color: #636e72;">
                <strong>Meta Ads:</strong>
                Hook Rate: <span style="color: #00b894;">🟢>15%</span> <span style="color: #fdcb6e;">🟡8-15%</span> <span style="color: #e17055;">🔴<8%</span>
            </div>
            <div style="color: #636e72;">
                CTR: <span style="color: #00b894;">🟢>2%</span> <span style="color: #fdcb6e;">🟡1-2%</span> <span style="color: #e17055;">🔴<1%</span>
            </div>
            <div style="color: #636e72;">
                Meta Conv.: <span style="color: #00b894;">🟢>10%</span> <span style="color: #fdcb6e;">🟡5-10%</span> <span style="color: #e17055;">🔴<5%</span>
            </div>
        </div>

        <div style="display: flex; flex-wrap: wrap; gap: 16px; margin-top: 8px;">
            <div style="color: #636e72;">
                <strong>Costs:</strong>
                CPA: <span style="color: #00b894;">🟢<€100</span> <span style="color: #fdcb6e;">🟡€100-200</span> <span style="color: #e17055;">🔴>€200</span>
            </div>
            <div style="color: #636e72;">
                CPL: <span style="color: #00b894;">🟢<€20</span> <span style="color: #fdcb6e;">🟡€20-40</span> <span style="color: #e17055;">🔴>€40</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_benchmark_legend():
    """Original benchmark legend for backward compatibility"""
    display_enhanced_benchmark_legend()

def display_enhanced_kpi_cards(valid_results, meta_data=None):
    """Enhanced KPI cards including Meta Ads metrics"""
    # HighLevel metrics
    total_rdv = sum([r['metrics']['totalRDVPlanifies'] for r in valid_results])
    total_confirmed = sum([r['metrics']['rdvConfirmes'] for r in valid_results])
    total_showup = sum([r['metrics']['showUp'] for r in valid_results])
    avg_confirmation = (total_confirmed / total_rdv * 100) if total_rdv > 0 else 0
    avg_conversion = (total_showup / total_confirmed * 100) if total_confirmed > 0 else 0

    # Meta Ads metrics (if available)
    if meta_data:
        total_spend = sum([m.get('spend', 0) for m in meta_data])
        total_meta_leads = sum([m.get('meta_leads', 0) for m in meta_data])
        total_impressions = sum([m.get('impressions', 0) for m in meta_data])
        total_clicks = sum([m.get('inline_link_clicks', 0) for m in meta_data])
        total_video_30s = sum([m.get('video_30_sec_watched', 0) for m in meta_data])

        avg_hook_rate = (total_video_30s / total_impressions * 100) if total_impressions > 0 else 0
        avg_meta_conv = (total_meta_leads / total_clicks * 100) if total_clicks > 0 else 0
        avg_cpa = sum([m.get('cpa', 0) for m in meta_data if m.get('cpa', 0) > 0]) / len([m for m in meta_data if m.get('cpa', 0) > 0]) if any(m.get('cpa', 0) > 0 for m in meta_data) else 0
        avg_cpl = sum([m.get('cpl', 0) for m in meta_data if m.get('cpl', 0) > 0]) / len([m for m in meta_data if m.get('cpl', 0) > 0]) if any(m.get('cpl', 0) > 0 for m in meta_data) else 0

        # Display enhanced cards with Meta metrics
        st.markdown("#### 🏢 HighLevel Performance")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card("Total RDV", f"{total_rdv:,}", "volume"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card("Confirmed", f"{total_confirmed:,}", "volume"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card("Show Up", f"{total_showup:,}", "volume"), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card("Avg Conversion", f"{avg_conversion:.1f}%", "conversion"), unsafe_allow_html=True)

        st.markdown("#### 📱 Meta Ads Performance")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card("Total Impressions", f"{total_impressions:,}", "volume"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card("Meta Leads", f"{total_meta_leads:,}", "volume"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card("Hook Rate", f"{avg_hook_rate:.1f}%", "hook_rate"), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card("Meta Conv.", f"{avg_meta_conv:.1f}%", "meta_conversion"), unsafe_allow_html=True)

        st.markdown("#### 💰 Cost Performance")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card("Total Spend", f"€{total_spend:,.0f}", "volume"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card("Avg CPA", f"€{avg_cpa:.0f}", "cpa"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card("Avg CPL", f"€{avg_cpl:.0f}", "cpl"), unsafe_allow_html=True)
        with col4:
            lead_to_sale = (total_showup / total_meta_leads * 100) if total_meta_leads > 0 else 0
            st.markdown(create_metric_card("Lead→Sale", f"{lead_to_sale:.1f}%", "conversion"), unsafe_allow_html=True)
    else:
        # Original KPI cards for HighLevel only
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card("Total RDV", f"{total_rdv:,}", "volume"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card("Confirmed", f"{total_confirmed:,}", "volume"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card("Show Up", f"{total_showup:,}", "volume"), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card("Avg Conversion", f"{avg_conversion:.1f}%", "conversion"), unsafe_allow_html=True)

def display_kpi_cards(valid_results):
    """Original KPI cards function for backward compatibility"""
    display_enhanced_kpi_cards(valid_results)

def display_combined_performance_table(combined_data):
    """Display combined HighLevel + Meta Ads performance table with color coding"""
    if not combined_data:
        st.warning("No combined performance data available.")
        return None

    # Prepare data for display
    table_data = []
    for center in combined_data:
        if center.get('has_meta_error') or center.get('has_created_error'):
            continue  # Skip centers with errors

        row = {
            "Center": center['centerName'],
            "City": center['city'],
            # Meta Ads metrics
            "Impressions": center.get('impressions', 0),
            "Clicks": center.get('inline_link_clicks', 0),
            "Video 30s": center.get('video_30_sec_watched', 0),
            "Meta Leads": center.get('meta_leads', 0),
            "Hook Rate": f"{center.get('hook_rate', 0):.1f}%",
            "Meta Conv. Rate": f"{center.get('meta_conversion_rate', 0):.1f}%",
            "CTR": f"{center.get('ctr', 0):.2f}%",
            "Spend": f"€{center.get('spend', 0):.0f}",
            "CPL": f"€{center.get('cpl', 0):.0f}",
            "CPA": f"€{center.get('cpa', 0):.0f}",
            # HighLevel metrics
            "Total RDV": center.get('total_created', 0),
            "Concrétisé": center.get('concretise', 0),
            "Confirmation Rate": f"{center.get('confirmation_rate', 0):.1f}%",
            "Conversion Rate": f"{center.get('conversion_rate', 0):.1f}%",
            "Lead→RDV Rate": f"{center.get('lead_to_appointment_rate', 0):.1f}%",
            "Lead→Sale Rate": f"{center.get('lead_to_sale_rate', 0):.1f}%"
        }
        table_data.append(row)

    if not table_data:
        st.warning("No valid combined performance data to display.")
        return None

    df = pd.DataFrame(table_data)

    # Define metric columns for color coding
    metric_columns = {
        "Hook Rate": "hook_rate",
        "Meta Conv. Rate": "meta_conversion", 
        "CTR": "ctr",
        "Confirmation Rate": "confirmation",
        "Conversion Rate": "conversion",
        "Lead→RDV Rate": "lead_conversion",
        "Lead→Sale Rate": "lead_conversion"
    }

    # Apply color coding
    styled_df = create_colored_dataframe(df, metric_columns)

    st.subheader("📊 Combined Performance Analysis")
    st.dataframe(styled_df, use_container_width=True, height=400)

    return df

def display_detailed_metrics_table(valid_results):
    """Display detailed metrics table with color coding"""
    detailed_data = []
    for r in valid_results:
        row = {
            "Center": r['centerName'],
            "City": r['city'],
            "Total RDV": r['metrics']['totalRDVPlanifies'],
            "Confirmed": r['metrics']['rdvConfirmes'],
            "Show Up": r['metrics']['showUp'],
            "Confirmation Rate": r['metrics']['tauxConfirmation'],
            "Cancellation Rate": r['metrics']['tauxAnnulation'],
            "No Show Rate": r['metrics']['tauxNoShow'],
            "Presence Rate": r['metrics']['tauxPresence'],
            "Conversion Rate": r['metrics']['tauxConversion'],
            "Annulé": r['metrics']['details']['annule'],
            "Confirmé": r['metrics']['details']['confirme'],
            "Pas Venu": r['metrics']['details']['pasVenu'],
            "Présent": r['metrics']['details']['present'],
            "Concrétisé": r['metrics']['details']['concretise'],
            "Non Confirmé": r['metrics']['details']['nonConfirme'],
            # Add new stage details if available
            "Non Qualifié": r['metrics']['details'].get('nonQualifie', 0),
            "Sans Réponse": r['metrics']['details'].get('sansReponse', 0)
        }
        detailed_data.append(row)

    df = pd.DataFrame(detailed_data)

    metric_columns = {
        "Confirmation Rate": "confirmation",
        "Cancellation Rate": "cancellation", 
        "No Show Rate": "no_answer",
        "Presence Rate": "show_up",
        "Conversion Rate": "conversion"
    }

    styled_df = create_colored_dataframe(df, metric_columns)

    st.dataframe(styled_df, use_container_width=True)

    return df

def display_meta_ads_performance_table(meta_data):
    """Display Meta Ads performance table with color coding"""
    if not meta_data:
        st.warning("No Meta Ads data available.")
        return None

    table_data = []
    for center in meta_data:
        metrics = center.get('metrics', {})
        if 'error' in metrics:
            continue  # Skip centers with errors

        row = {
            "Center": center['centerName'],
            "City": center['city'],
            "Impressions": metrics.get('impressions', 0),
            "Clicks": metrics.get('inline_link_clicks', 0),
            "Video 30s Views": metrics.get('video_30_sec_watched', 0),
            "Leads": metrics.get('leads', 0),
            "Hook Rate": f"{metrics.get('hook_rate', 0):.2f}%",
            "Meta Conv. Rate": f"{metrics.get('conversion_rate', 0):.2f}%",
            "CTR": f"{metrics.get('ctr', 0):.2f}%",
            "Spend": f"€{metrics.get('spend', 0):.2f}",
            "CPM": f"€{metrics.get('cpm', 0):.2f}",
            "CPR": f"€{metrics.get('cpr', 0):.2f}"
        }
        table_data.append(row)

    if not table_data:
        st.warning("No valid Meta Ads data to display.")
        return None

    df = pd.DataFrame(table_data)

    # Define metric columns for color coding
    metric_columns = {
        "Hook Rate": "hook_rate",
        "Meta Conv. Rate": "meta_conversion",
        "CTR": "ctr"
    }

    # Apply color coding
    styled_df = create_colored_dataframe(df, metric_columns)

    st.subheader("📱 Meta Ads Performance")
    st.dataframe(styled_df, use_container_width=True)

    return df

def display_benchmark_analysis_cards(valid_results):
    """Display benchmark analysis with colored cards for each center"""
    for r in valid_results:
        st.subheader(f"🏢 {r['centerName']} - {r['city']}")

        col1, col2, col3, col4, col5 = st.columns(5)
        metrics = r['metrics']

        with col1:
            st.markdown(create_metric_card("Confirmation", metrics['tauxConfirmation'], "confirmation"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card("Show Up", metrics['tauxPresence'], "show_up"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card("Conversion", metrics['tauxConversion'], "conversion"), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card("Cancellation", metrics['tauxAnnulation'], "cancellation"), unsafe_allow_html=True)
        with col5:
            st.markdown(create_metric_card("No Show", metrics['tauxNoShow'], "no-show"), unsafe_allow_html=True)

def display_enhanced_benchmark_analysis_cards(valid_results, meta_data=None):
    """Enhanced benchmark analysis including Meta Ads metrics"""
    for i, r in enumerate(valid_results):
        st.subheader(f"🏢 {r['centerName']} - {r['city']}")

        # HighLevel metrics
        st.markdown("**📊 HighLevel Performance**")
        col1, col2, col3, col4, col5 = st.columns(5)
        metrics = r['metrics']

        with col1:
            st.markdown(create_metric_card("Confirmation", metrics['tauxConfirmation'], "confirmation"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card("Show Up", metrics['tauxPresence'], "show_up"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card("Conversion", metrics['tauxConversion'], "conversion"), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card("Cancellation", metrics['tauxAnnulation'], "cancellation"), unsafe_allow_html=True)
        with col5:
            st.markdown(create_metric_card("No Show", metrics['tauxNoShow'], "no-show"), unsafe_allow_html=True)

        # Meta Ads metrics (if available)
        if meta_data and i < len(meta_data):
            meta_metrics = meta_data[i].get('metrics', {})
            if 'error' not in meta_metrics:
                st.markdown("**📱 Meta Ads Performance**")
                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    hook_rate = f"{meta_metrics.get('hook_rate', 0):.1f}%"
                    st.markdown(create_metric_card("Hook Rate", hook_rate, "hook_rate"), unsafe_allow_html=True)
                with col2:
                    meta_conv = f"{meta_metrics.get('conversion_rate', 0):.1f}%"
                    st.markdown(create_metric_card("Meta Conv.", meta_conv, "meta_conversion"), unsafe_allow_html=True)
                with col3:
                    ctr = f"{meta_metrics.get('ctr', 0):.2f}%"
                    st.markdown(create_metric_card("CTR", ctr, "ctr"), unsafe_allow_html=True)
                with col4:
                    cpl = f"€{meta_metrics.get('cpr', 0):.0f}"  # Using CPR as CPL equivalent
                    st.markdown(create_metric_card("CPL", cpl, "cpl"), unsafe_allow_html=True)
                with col5:
                    spend = f"€{meta_metrics.get('spend', 0):.0f}"
                    st.markdown(create_metric_card("Spend", spend, "volume"), unsafe_allow_html=True)

        st.markdown("---")

def display_stage_analysis_table(valid_results):
    """Display stage analysis table with color coding"""
    all_stages = set()
    for r in valid_results:
        if 'stageStats' in r:
            all_stages.update(r['stageStats'].keys())

    stage_data = []
    for r in valid_results:
        row = {
            "Center": r['centerName'],
            "City": r['city'],
            "Total RDV": r['metrics']['totalRDVPlanifies']
        }
        for stage in sorted(all_stages):
            row[stage] = r.get('stageStats', {}).get(stage, 0)
        stage_data.append(row)

    if stage_data:
        stage_df = pd.DataFrame(stage_data)
        st.dataframe(stage_df, use_container_width=True)
        return stage_df
    return None

def create_performance_comparison_table(highlevel_data, meta_data):
    """Create a side-by-side comparison table of HighLevel vs Meta Ads performance"""
    if not highlevel_data or not meta_data:
        return None

    comparison_data = []

    for hl_center in highlevel_data:
        center_name = hl_center['centerName']

        # Find matching Meta data
        meta_center = next((m for m in meta_data if m['centerName'] == center_name), None)

        if meta_center and 'error' not in meta_center.get('metrics', {}):
            hl_metrics = hl_center['metrics']
            meta_metrics = meta_center['metrics']

            row = {
                "Center": center_name,
                "City": hl_center['city'],
                # HighLevel
                "HL Total RDV": hl_metrics['totalRDVPlanifies'],
                "HL Confirmed": hl_metrics['rdvConfirmes'],
                "HL Show Up": hl_metrics['showUp'],
                "HL Conversion": hl_metrics['tauxConversion'],
                # Meta Ads
                "Meta Leads": meta_metrics.get('leads', 0),
                "Meta Spend": f"€{meta_metrics.get('spend', 0):.0f}",
                "Hook Rate": f"{meta_metrics.get('hook_rate', 0):.1f}%",
                "Meta Conv.": f"{meta_metrics.get('conversion_rate', 0):.1f}%",
                # Combined
                "Lead→RDV": f"{(hl_metrics['totalRDVPlanifies'] / meta_metrics.get('leads', 1) * 100):.1f}%" if meta_metrics.get('leads', 0) > 0 else "0%",
                "CPA": f"€{(meta_metrics.get('spend', 0) / hl_metrics.get('showUp', 1)):.0f}" if hl_metrics.get('showUp', 0) > 0 else "€0"
            }
            comparison_data.append(row)

    if comparison_data:
        df = pd.DataFrame(comparison_data)

        # Color coding for key metrics
        metric_columns = {
            "HL Conversion": "conversion",
            "Hook Rate": "hook_rate", 
            "Meta Conv.": "meta_conversion",
            "Lead→RDV": "lead_conversion"
        }

        styled_df = create_colored_dataframe(df, metric_columns)

        st.subheader("🔄 HighLevel vs Meta Ads Comparison")
        st.dataframe(styled_df, use_container_width=True)

        return df

    return None
