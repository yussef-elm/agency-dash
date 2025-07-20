
import streamlit as st
from api_client import fetch_centers_data
from charts import create_scatter_plot, create_performance_distribution_chart

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

    st.subheader("📈 Performance Trends")

    col1, col2 = st.columns(2)

    with col1:
        fig = create_scatter_plot(valid_results)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = create_performance_distribution_chart(valid_results)
        st.plotly_chart(fig, use_container_width=True)
