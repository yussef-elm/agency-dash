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
                
                # Display summary metrics
                summary = get_performance_summary(combined_data)
                if 'error' not in summary:
                    st.markdown("#### 📊 Performance Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Spend", f"€{summary['total_spend']:.2f}")
                    with col2:
                        st.metric("Avg CPA", f"€{summary['avg_cpa']:.2f}")
                    with col3:
                        st.metric("Avg CPL", f"€{summary['avg_cpl']:.2f}")
                    with col4:
                        st.metric("Lead→Sale Rate", f"{summary['overall_lead_to_sale']:.1f}%")
                
                # Display detailed table
                st.markdown("#### 📋 Detailed Performance Table")
                display_data = format_combined_data_for_display(combined_data)
                
                if display_data:
                    st.dataframe(
                        display_data, 
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Add download button for the data
                    import pandas as pd
                    df = pd.DataFrame(display_data)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Combined Data as CSV",
                        data=csv,
                        file_name=f"combined_performance_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No combined data available for the selected centers and date range.")
                
                # Show errors if any
                errors = [c for c in combined_data if c['has_meta_error'] or c['has_created_error']]
                if errors:
                    with st.expander(f"⚠️ {len(errors)} centers have data issues"):
                        for error_center in errors:
                            if error_center['has_meta_error']:
                                st.error(f"**{error_center['centerName']}** - Meta error: {error_center['meta_error']}")
                            if error_center['has_created_error']:
                                st.error(f"**{error_center['centerName']}** - HighLevel error: {error_center['created_error']}")
                
            except Exception as e:
                st.error(f"Error fetching combined data: {str(e)}")
                st.info("💡 The HighLevel performance data above is still available.")
    
    else:
        # Show info about combined analysis when no access token
        with st.expander("💡 Want to see Cost Per Acquisition (CPA) analysis?"):
            st.info("""
            **Combined Performance Analysis** shows:
            - Cost Per Acquisition (CPA) = Meta Spend ÷ HighLevel Sales
            - Cost Per Lead (CPL) = Meta Spend ÷ Meta Leads  
            - Lead to Sale Conversion Rate
            - Lead to Appointment Rate
            
            To enable this feature, please provide your Meta Ads access token in the app configuration.
            """)