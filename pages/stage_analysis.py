import streamlit as st
from api_client import fetch_centers_data
from components import display_stage_analysis_table
from charts import create_stage_distribution_chart
import pandas as pd

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

    st.subheader("📊 Stage Statistics")

    stage_df = display_stage_analysis_table(valid_results)

    if stage_df is not None:
        # Ensure 'sans_reponse' and 'non_qualifie' columns exist with default 0
        for col in ['sans_reponse', 'non_qualifie']:
            if col not in stage_df.columns:
                stage_df[col] = 0

        # List all stage columns except identifiers
        all_stages = [col for col in stage_df.columns if col not in ["Center", "City", "Total RDV"]]

        # Sum totals for each stage
        stage_totals = {stage: stage_df[stage].sum() for stage in all_stages}

        fig = create_stage_distribution_chart(stage_totals)
        if fig:
            st.plotly_chart(fig, use_container_width=True)