import streamlit as st
from api_client import (
    fetch_centers_data, 
    fetch_combined_performance_data, 
    format_combined_data_for_display, 
    get_performance_summary
)
from components import display_kpi_cards
from charts import create_performance_bar_chart, create_performance_radar_chart
import pandas as pd

# --- Utility functions for formatting and column management ---

def format_currency(value):
    try:
        return f"€{float(value):,.2f}"
    except Exception:
        return "€0.00"

def format_percentage(value):
    try:
        return f"{float(value):.2f}%"
    except Exception:
        return "0.00%"

def format_number(value):
    try:
        return f"{int(value):,}"
    except Exception:
        return "0"

def ensure_all_columns(df, expected_columns):
    for col, default in expected_columns.items():
        if col not in df.columns:
            df[col] = default
    return df

def show(selected_centers, start_date, end_date, access_token=None):
    with st.spinner("Fetching performance data..."):
        results = fetch_centers_data(start_date.isoformat(), end_date.isoformat(), selected_centers)

    valid_results = [r for r in results if 'error' not in r]
    error_results = [r for r in results if 'error' in r]

    if error_results:
        st.error(f"Errors occurred for {len(error_results)} centers:")
        for error in error_results:
            st.error(f"- {error['centerName']}: {error['error']}")

    if not valid_results:
        st.error("No valid data retrieved. Please check your API keys and try again.")
        st.stop()

    st.markdown(f"**Analysis Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    st.markdown(f"**Centers Analyzed:** {len(valid_results)}")

    display_kpi_cards(valid_results)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Performance by Center")
        fig = create_performance_bar_chart(valid_results)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("🎯 Performance Radar")
        fig = create_performance_radar_chart(valid_results)
        st.plotly_chart(fig, use_container_width=True)

    # Add Combined Performance Data Table
    st.markdown("---")  # Separator line

    if access_token:
        st.subheader("💰 Combined Performance Analysis (Meta Ads + HighLevel)")

        with st.spinner("Fetching combined Meta Ads + HighLevel data..."):
            try:
                combined_data = fetch_combined_performance_data(
                    start_date.isoformat(), 
                    end_date.isoformat(), 
                    selected_centers, 
                    access_token
                )

                # Display summary metrics with enhanced KPIs
                summary = get_performance_summary(combined_data)
                if 'error' not in summary:
                    st.markdown("#### 📊 Performance Summary")

                    # First row of metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Spend", format_currency(summary['total_spend']))
                    with col2:
                        st.metric("Total Impressions", format_number(summary['total_impressions']))
                    with col3:
                        st.metric("Total Clicks", format_number(summary['total_clicks']))
                    with col4:
                        st.metric("Total Meta Leads", format_number(summary['total_meta_leads']))

                    # Second row of metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Avg CPA", format_currency(summary['avg_cpa']))
                    with col2:
                        st.metric("Avg CPL", format_currency(summary['avg_cpl']))
                    with col3:
                        st.metric("Overall Hook Rate", format_percentage(summary['overall_hook_rate']))
                    with col4:
                        st.metric("Overall Meta Conv. Rate", format_percentage(summary['overall_meta_conversion_rate']))

                    # Third row of metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Lead→RDV Rate", format_percentage(summary['overall_lead_to_appointment']))
                    with col2:
                        st.metric("Lead→Sale Rate", format_percentage(summary['overall_lead_to_sale']))
                    with col3:
                        st.metric("Avg CPM", format_currency(summary['avg_cpm']))
                    with col4:
                        st.metric("Avg CTR", format_percentage(summary['avg_ctr']))

                # Display detailed table with enhanced columns
                st.markdown("#### 📋 Detailed Performance Table")
                display_data = format_combined_data_for_display(combined_data)

                # --- Ensure all columns are present, including those needed for display ---
                expected_columns = {
                    'Centre': '',
                    'Ville': '',
                    'Dépense (€)': 0.0,
                    'CPL (€)': 0.0,
                    'CPA - Coût/Concrétisation (€)': 0.0,
                    'CPR (€)': 0.0,
                    'CPM (€)': 0.0,
                    'Leads Meta': 0,
                    'Concrétisé': 0,
                    'Impressions': 0,
                    'Clics': 0,
                    'Vues 30s': 0,
                    'Hook Rate (%)': 0.0,
                    'Meta Conv. Rate (%)': 0.0,
                    'CTR (%)': 0.0,
                    'Lead→RDV (%)': 0.0,
                    'Lead→Sale (%)': 0.0,
                    'Taux Confirmation (%)': 0.0,
                    'Taux Conversion (%)': 0.0,
                    'Taux Annulation (%)': 0.0,
                    'Taux No-Show (%)': 0.0,
                    'Nb RDV': 0
                }
                # Convert to DataFrame and ensure all columns
                df = pd.DataFrame(display_data)
                df = ensure_all_columns(df, expected_columns)

                # Format for display
                display_df = df.copy()
                for col in ['Dépense (€)', 'CPL (€)', 'CPA - Coût/Concrétisation (€)', 'CPR (€)', 'CPM (€)']:
                    display_df[col] = display_df[col].apply(format_currency)
                for col in ['Hook Rate (%)', 'Meta Conv. Rate (%)', 'CTR (%)', 'Lead→RDV (%)', 'Lead→Sale (%)', 'Taux Confirmation (%)', 'Taux Conversion (%)', 'Taux Annulation (%)', 'Taux No-Show (%)']:
                    display_df[col] = display_df[col].apply(format_percentage)
                for col in ['Impressions', 'Clics', 'Vues 30s', 'Leads Meta', 'Concrétisé', 'Nb RDV']:
                    display_df[col] = display_df[col].apply(format_number)

                # Create tabs for different views of the data
                tab1, tab2, tab3 = st.tabs(["📊 Complete View", "💰 Cost Metrics", "📈 Conversion Metrics"])

                with tab1:
                    st.markdown("**Complete performance data with all metrics**")
                    st.dataframe(
                        display_df, 
                        use_container_width=True,
                        hide_index=True,
                        height=400
                    )

                with tab2:
                    # Cost-focused view
                    cost_columns = ['Centre', 'Ville', 'Dépense (€)', 'CPL (€)', 'CPA - Coût/Concrétisation (€)', 
                                  'CPR (€)', 'CPM (€)', 'Leads Meta', 'Concrétisé']
                    st.dataframe(display_df[cost_columns], use_container_width=True, hide_index=True)

                with tab3:
                    # Conversion-focused view
                    conv_columns = ['Centre', 'Ville', 'Hook Rate (%)', 'Meta Conv. Rate (%)', 'CTR (%)',
                                  'Lead→RDV (%)', 'Lead→Sale (%)', 'Taux Confirmation (%)', 'Taux Conversion (%)']
                    st.dataframe(display_df[conv_columns], use_container_width=True, hide_index=True)

                # Enhanced download options
                st.markdown("#### 📥 Download Options")
                col1, col2, col3 = st.columns(3)

                with col1:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📄 Download Complete Data (CSV)",
                        data=csv,
                        file_name=f"complete_performance_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

                with col2:
                    # Cost metrics only
                    cost_csv = df[cost_columns].to_csv(index=False)
                    st.download_button(
                        label="💰 Download Cost Metrics (CSV)",
                        data=cost_csv,
                        file_name=f"cost_metrics_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

                with col3:
                    # Conversion metrics only
                    conv_csv = df[conv_columns].to_csv(index=False)
                    st.download_button(
                        label="📈 Download Conversion Metrics (CSV)",
                        data=conv_csv,
                        file_name=f"conversion_metrics_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

                # Enhanced error reporting
                errors = [c for c in combined_data if c.get('has_meta_error') or c.get('has_created_error')]
                if errors:
                    with st.expander(f"⚠️ {len(errors)} centers have data issues", expanded=False):
                        for error_center in errors:
                            st.markdown(f"**{error_center['centerName']} ({error_center['city']})**")
                            if error_center.get('has_meta_error'):
                                st.error(f"📱 Meta Ads Error: {error_center.get('meta_error', '')}")
                            if error_center.get('has_created_error'):
                                st.error(f"🏢 HighLevel Error: {error_center.get('created_error', '')}")
                            st.markdown("---")

                # Performance insights
                if 'error' not in summary and summary['total_centers'] > 1:
                    st.markdown("#### 💡 Performance Insights")

                    # Find best and worst performers
                    valid_centers = [c for c in combined_data if not c.get('has_meta_error') and not c.get('has_created_error')]

                    if len(valid_centers) >= 2:
                        # Best CPA
                        best_cpa = min(valid_centers, key=lambda x: x.get('cpa', float('inf')) if x.get('cpa', 0) > 0 else float('inf'))
                        worst_cpa = max(valid_centers, key=lambda x: x.get('cpa', 0))

                        # Best conversion rates
                        best_hook = max(valid_centers, key=lambda x: x.get('hook_rate', 0))
                        best_meta_conv = max(valid_centers, key=lambda x: x.get('meta_conversion_rate', 0))
                        best_lead_to_sale = max(valid_centers, key=lambda x: x.get('lead_to_sale_rate', 0))

                        col1, col2 = st.columns(2)

                        with col1:
                            st.success(f"🏆 **Best CPA**: {best_cpa['centerName']} (€{best_cpa.get('cpa', 0):.2f})")
                            st.success(f"🎯 **Best Hook Rate**: {best_hook['centerName']} ({best_hook.get('hook_rate', 0):.2f}%)")
                            st.success(f"📈 **Best Meta Conv. Rate**: {best_meta_conv['centerName']} ({best_meta_conv.get('meta_conversion_rate', 0):.2f}%)")

                        with col2:
                            if worst_cpa.get('cpa', 0) > 0:
                                st.warning(f"⚠️ **Highest CPA**: {worst_cpa['centerName']} (€{worst_cpa.get('cpa', 0):.2f})")
                            st.info(f"🎖️ **Best Lead→Sale**: {best_lead_to_sale['centerName']} ({best_lead_to_sale.get('lead_to_sale_rate', 0):.2f}%)")
                            st.info(f"💰 **Total Investment**: {format_currency(summary['total_spend'])} across {summary['total_centers']} centers")

            except Exception as e:
                st.error(f"Error fetching combined data: {str(e)}")
                st.info("💡 The HighLevel performance data above is still available.")

                # Show detailed error for debugging
                with st.expander("🔧 Technical Details"):
                    st.code(str(e))

    else:
        # Enhanced info about combined analysis when no access token
        with st.expander("💡 Want to see Advanced Performance Analysis?", expanded=True):
            st.info("""
            **🚀 Combined Performance Analysis** includes:

            **📊 Meta Ads Metrics:**
            - Impressions, Clicks, Video Views (30s)
            - Hook Rate (30s video views ÷ impressions)
            - Meta Conversion Rate (leads ÷ clicks)
            - CPM, CTR, CPR

            **💰 Cost Analysis:**
            - Cost Per Acquisition (CPA) = Meta Spend ÷ HighLevel Sales
            - Cost Per Lead (CPL) = Meta Spend ÷ Meta Leads

            **📈 Conversion Funnels:**
            - Lead → Appointment Rate
            - Lead → Sale Conversion Rate
            - Complete funnel analysis

            **🎯 Performance Insights:**
            - Best/worst performing centers
            - Optimization recommendations
            - ROI analysis

            To enable this feature, please provide your Meta Ads access token in the app configuration.
            """)

            # Show what's available without token
            st.markdown("**Currently Available (HighLevel Only):**")
            st.markdown("- Appointment booking rates")
            st.markdown("- Confirmation and cancellation rates")
            st.markdown("- Show-up and conversion rates")
            st.markdown("- Stage-by-stage pipeline analysis")