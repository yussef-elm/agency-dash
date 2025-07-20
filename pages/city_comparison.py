
import streamlit as st
from api_client import fetch_centers_data
from charts import create_city_comparison_charts
from components import create_metric_card

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

    cities_in_data = list(set([r['city'] for r in valid_results]))

    for city in cities_in_data:
        st.subheader(f"🏙️ {city}")
        city_centers = [r for r in valid_results if r['city'] == city]

        if len(city_centers) > 1:
            charts = create_city_comparison_charts(city_centers, city)

            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(charts['rdv'], use_container_width=True)
            with col2:
                st.plotly_chart(charts['showup'], use_container_width=True)
        else:
            st.info(f"Only one center in {city}")
            center = city_centers[0]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(create_metric_card("RDV", f"{center['metrics']['totalRDVPlanifies']:,}", "volume"), unsafe_allow_html=True)
            with col2:
                st.markdown(create_metric_card("Confirmed", f"{center['metrics']['rdvConfirmes']:,}", "volume"), unsafe_allow_html=True)
            with col3:
                st.markdown(create_metric_card("Show Up", f"{center['metrics']['showUp']:,}", "volume"), unsafe_allow_html=True)
