
import streamlit as st
import io
import pandas as pd
from api_client import fetch_centers_data_created
from components import display_kpi_cards, display_detailed_metrics_table
from charts import create_performance_bar_chart, create_performance_radar_chart

def show(selected_centers, start_date, end_date):
    with st.spinner("Fetching created leads data..."):
        results = fetch_centers_data_created(start_date.isoformat(), end_date.isoformat(), selected_centers)
    valid_results = [r for r in results if 'error' not in r]
    error_results = [r for r in results if 'error' in r]
    if error_results:
        st.error(f"Errors occurred for {len(error_results)} centers:")
        for error in error_results:
            st.error(f"- {error['centerName']}: {error['error']}")
    if not valid_results:
        st.error("No valid data retrieved for created leads. Please check your API keys and try again.")
        st.stop()

    st.markdown("---")
    st.markdown("### 🆕 Created Leads Analysis")
    st.markdown("*All metrics below are based on the **createdAt** field (when leads were first created)*")

    st.markdown(f"**Analysis Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    st.markdown(f"**Centers Analyzed:** {len(valid_results)}")

    display_kpi_cards(valid_results)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Created Leads by Center")
        fig = create_performance_bar_chart(valid_results)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🎯 Performance Radar (Created)")
        fig = create_performance_radar_chart(valid_results)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Detailed Created Leads Metrics")
    df = display_detailed_metrics_table(valid_results)

    st.subheader("📤 Export Created Leads Data")
    col1, col2 = st.columns(2)

    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            "📋 Download CSV",
            csv,
            f"created_leads_report_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.csv",
            "text/csv"
        )

    with col2:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Created Leads', index=False)

        st.download_button(
            "📊 Download Excel",
            buffer.getvalue(),
            f"created_leads_report_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
