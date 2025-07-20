
import streamlit as st
from datetime import datetime, timedelta
from config import CENTERS, CUSTOM_CSS,ACCESS_TOKEN
from components import display_benchmark_legend

# Import page modules
from pages import (
    performance_overview,
    benchmark_analysis,
    city_comparison,
    detailed_metrics,
    stage_analysis,
    trend_analysis,
    created_leads_analysis,
    appointment_status_analysis,
    meta_metrics
)

st.set_page_config(page_title="Agency Clients Performance", page_icon="🚀", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st.markdown("""
    <style>
    /* Hide the Streamlit multipage navigation sidebar */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Agency Clients Performance Dashboard")
display_benchmark_legend()

page = st.sidebar.selectbox("Select Page", [
    "Performance Overview", "Benchmark Analysis", "City Comparison", 
    "Detailed Metrics", "Stage Analysis", "Trend Analysis", 
    "Created Leads Analysis", "Appointment Status Analysis","Meta Ads Metrics"
])

# Date and center selection common to all pages
start_date = st.sidebar.date_input("Start Date", datetime.now().date() - timedelta(days=30))
end_date = st.sidebar.date_input("End Date", datetime.now().date())
cities = list(set([center['city'] for center in CENTERS]))
selected_cities = st.sidebar.multiselect("Select Cities", cities, default=cities)
center_names = [center['centerName'] for center in CENTERS if center['city'] in selected_cities]
selected_centers = st.sidebar.multiselect("Select Centers", center_names, default=center_names)
access_token=ACCESS_TOKEN
if not selected_centers:
    st.warning("Please select at least one center to analyze.")
    st.stop()

# Route to page modules
if page == "Performance Overview":
    performance_overview.show(selected_centers, start_date, end_date,access_token)
elif page == "Benchmark Analysis":
    benchmark_analysis.show(selected_centers, start_date, end_date)
elif page == "City Comparison":
    city_comparison.show(selected_centers, start_date, end_date)
elif page == "Detailed Metrics":
    detailed_metrics.show(selected_centers, start_date, end_date)
elif page == "Stage Analysis":
    stage_analysis.show(selected_centers, start_date, end_date)
elif page == "Trend Analysis":
    trend_analysis.show(selected_centers, start_date, end_date)
elif page == "Created Leads Analysis":
    created_leads_analysis.show(selected_centers, start_date, end_date)
elif page == "Appointment Status Analysis":
    appointment_status_analysis.show(selected_centers, start_date, end_date)
elif page == "Meta Ads Metrics":  # <-- Add this route
    meta_metrics.show(selected_centers, start_date, end_date,access_token)

st.markdown("---")
st.markdown("*Real-time performance data from HighLevel API*")
