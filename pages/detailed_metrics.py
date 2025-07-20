
import streamlit as st
import io
import pandas as pd
from api_client import fetch_centers_data
from components import display_detailed_metrics_table

def show(selected_centers, start_date, end_date):
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

    st.subheader("📋 Detailed Performance Metrics")

    df = display_detailed_metrics_table(valid_results)

    st.subheader("📤 Export Data")
    col1, col2 = st.columns(2)

    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            "📋 Download CSV",
            csv,
            f"performance_report_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.csv",
            "text/csv"
        )

    with col2:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Performance', index=False)

        st.download_button(
            "📊 Download Excel",
            buffer.getvalue(),
            f"performance_report_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
