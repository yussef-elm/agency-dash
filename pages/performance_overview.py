import streamlit as st
from api_client import (
    fetch_centers_data, 
    fetch_combined_performance_data, 
    format_combined_data_for_display, 
    get_performance_summary
)
from components import display_kpi_cards
from charts import create_performance_bar_chart, create_performance_radar_chart

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
                        st.metric("Total Spend", f"€{summary['total_spend']:.2f}")
                    with col2:
                        st.metric("Total Impressions", f"{summary['total_impressions']:,}")
                    with col3:
                        st.metric("Total Clicks", f"{summary['total_clicks']:,}")
                    with col4:
                        st.metric("Total Meta Leads", f"{summary['total_meta_leads']:,}")

                    # Second row of metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Avg CPA", f"€{summary['avg_cpa']:.2f}")
                    with col2:
                        st.metric("Avg CPL", f"€{summary['avg_cpl']:.2f}")
                    with col3:
                        st.metric("Overall Hook Rate", f"{summary['overall_hook_rate']:.2f}%")
                    with col4:
                        st.metric("Overall Meta Conv. Rate", f"{summary['overall_meta_conversion_rate']:.2f}%")

                    # Third row of metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Lead→RDV Rate", f"{summary['overall_lead_to_appointment']:.1f}%")
                    with col2:
                        st.metric("Lead→Sale Rate", f"{summary['overall_lead_to_sale']:.1f}%")
                    with col3:
                        st.metric("Avg CPM", f"€{summary['avg_cpm']:.2f}")
                    with col4:
                        st.metric("Avg CTR", f"{summary['avg_ctr']:.2f}%")

                # Display detailed table with enhanced columns
                st.markdown("#### 📋 Detailed Performance Table")
                display_data = format_combined_data_for_display(combined_data)

                if display_data:
                    # Create tabs for different views of the data
                    tab1, tab2, tab3 = st.tabs(["📊 Complete View", "💰 Cost Metrics", "📈 Conversion Metrics"])

                    with tab1:
                        st.markdown("**Complete performance data with all metrics**")
                        st.dataframe(
                            display_data, 
                            use_container_width=True,
                            hide_index=True,
                            height=400
                        )

                    with tab2:
                        # Cost-focused view
                        cost_columns = ['Centre', 'Ville', 'Dépense (€)', 'CPL (€)', 'CPA - Coût/Concrétisation (€)', 
                                      'CPR (€)', 'CPM (€)', 'Leads Meta', 'Concrétisé']
                        cost_data = [{k: v for k, v in row.items() if k in cost_columns} for row in display_data]
                        st.dataframe(cost_data, use_container_width=True, hide_index=True)

                    with tab3:
                        # Conversion-focused view
                        conv_columns = ['Centre', 'Ville', 'Hook Rate (%)', 'Meta Conv. Rate (%)', 'CTR (%)',
                                      'Lead→RDV (%)', 'Lead→Sale (%)', 'Taux Confirmation (%)', 'Taux Conversion (%)']
                        conv_data = [{k: v for k, v in row.items() if k in conv_columns} for row in display_data]
                        st.dataframe(conv_data, use_container_width=True, hide_index=True)

                    # Enhanced download options
                    st.markdown("#### 📥 Download Options")
                    col1, col2, col3 = st.columns(3)

                    import pandas as pd
                    df = pd.DataFrame(display_data)

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
                        cost_df = df[['Centre', 'Ville', 'Dépense (€)', 'CPL (€)', 'CPA - Coût/Concrétisation (€)', 
                                    'CPR (€)', 'CPM (€)', 'Leads Meta', 'Concrétisé']]
                        cost_csv = cost_df.to_csv(index=False)
                        st.download_button(
                            label="💰 Download Cost Metrics (CSV)",
                            data=cost_csv,
                            file_name=f"cost_metrics_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )

                    with col3:
                        # Conversion metrics only
                        conv_df = df[['Centre', 'Ville', 'Hook Rate (%)', 'Meta Conv. Rate (%)', 'CTR (%)',
                                    'Lead→RDV (%)', 'Lead→Sale (%)', 'Taux Confirmation (%)', 'Taux Conversion (%)']]
                        conv_csv = conv_df.to_csv(index=False)
                        st.download_button(
                            label="📈 Download Conversion Metrics (CSV)",
                            data=conv_csv,
                            file_name=f"conversion_metrics_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )

                else:
                    st.warning("No combined data available for the selected centers and date range.")

                # Enhanced error reporting
                errors = [c for c in combined_data if c['has_meta_error'] or c['has_created_error']]
                if errors:
                    with st.expander(f"⚠️ {len(errors)} centers have data issues", expanded=False):
                        for error_center in errors:
                            st.markdown(f"**{error_center['centerName']} ({error_center['city']})**")
                            if error_center['has_meta_error']:
                                st.error(f"📱 Meta Ads Error: {error_center['meta_error']}")
                            if error_center['has_created_error']:
                                st.error(f"🏢 HighLevel Error: {error_center['created_error']}")
                            st.markdown("---")

                # Performance insights
                if 'error' not in summary and summary['total_centers'] > 1:
                    st.markdown("#### 💡 Performance Insights")

                    # Find best and worst performers
                    valid_centers = [c for c in combined_data if not c['has_meta_error'] and not c['has_created_error']]

                    if len(valid_centers) >= 2:
                        # Best CPA
                        best_cpa = min(valid_centers, key=lambda x: x['cpa'] if x['cpa'] > 0 else float('inf'))
                        worst_cpa = max(valid_centers, key=lambda x: x['cpa'])

                        # Best conversion rates
                        best_hook = max(valid_centers, key=lambda x: x['hook_rate'])
                        best_meta_conv = max(valid_centers, key=lambda x: x['meta_conversion_rate'])
                        best_lead_to_sale = max(valid_centers, key=lambda x: x['lead_to_sale_rate'])

                        col1, col2 = st.columns(2)

                        with col1:
                            st.success(f"🏆 **Best CPA**: {best_cpa['centerName']} (€{best_cpa['cpa']:.2f})")
                            st.success(f"🎯 **Best Hook Rate**: {best_hook['centerName']} ({best_hook['hook_rate']:.2f}%)")
                            st.success(f"📈 **Best Meta Conv. Rate**: {best_meta_conv['centerName']} ({best_meta_conv['meta_conversion_rate']:.2f}%)")

                        with col2:
                            if worst_cpa['cpa'] > 0:
                                st.warning(f"⚠️ **Highest CPA**: {worst_cpa['centerName']} (€{worst_cpa['cpa']:.2f})")
                            st.info(f"🎖️ **Best Lead→Sale**: {best_lead_to_sale['centerName']} ({best_lead_to_sale['lead_to_sale_rate']:.2f}%)")
                            st.info(f"💰 **Total Investment**: €{summary['total_spend']:.2f} across {summary['total_centers']} centers")

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
