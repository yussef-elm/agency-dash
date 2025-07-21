import streamlit as st
from datetime import datetime, timedelta
from config import CENTERS, CUSTOM_CSS, ACCESS_TOKEN
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

def check_login():
    """Check if user is logged in, show login form if not"""
    # Get credentials from secrets
    try:
        username = st.secrets["auth"]["username"]
        password = st.secrets["auth"]["password"]
    except KeyError:
        st.error("Authentication credentials not configured. Please contact the administrator.")
        st.stop()

    # Use session state to keep track of login
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        # Create a centered login form
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("### 🔐 Login Required")
            st.markdown("Please enter your credentials to access the dashboard.")

            with st.form("login_form"):
                user = st.text_input("Username", placeholder="Enter your username")
                pwd = st.text_input("Password", type="password", placeholder="Enter your password")
                login_button = st.form_submit_button("Login", use_container_width=True)

                if login_button:
                    if user == username and pwd == password:
                        st.session_state["logged_in"] = True
                        st.success("✅ Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")

        st.stop()  # Stop the app here if not logged in

def logout():
    """Logout function"""
    if st.button("🚪 Logout", key="logout_btn"):
        st.session_state["logged_in"] = False
        st.rerun()

# Call the login check at the very beginning
check_login()

# Set page config after login
st.set_page_config(page_title="Agency Clients Performance", page_icon="🚀", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none !important; }
    .sidebar-filters {
        background: linear-gradient(90deg, #f8fafc 60%, #e3f6fd 100%);
        border-radius: 14px;
        padding: 20px 18px 12px 18px;
        margin-bottom: 20px;
        box-shadow: 0 2px 12px #b2ebf233, 0 1.5px 8px #b2ebf255;
        border: 1.5px solid #e0f7fa;
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
    }
    </style>
""", unsafe_allow_html=True)

# Header with logout button
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🚀 Agency Clients Performance Dashboard")
with col2:
    logout()

display_benchmark_legend()

# --- Sidebar Filters ---
with st.sidebar:
    st.markdown('<div class="sidebar-filters">', unsafe_allow_html=True)
    st.markdown("### 🔎 Filter Data")

    # Navigation
    page = st.selectbox("📄 Select Page", [
        "Performance Overview", "Benchmark Analysis", "City Comparison", 
        "Detailed Metrics", "Stage Analysis", "Trend Analysis", 
        "Created Leads Analysis", "Appointment Status Analysis", "Meta Ads Metrics"
    ])

    st.markdown("#### 📅 Date Range")
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        start_date = st.date_input(
            "Start",
            value=datetime.now().date() - timedelta(days=30),
            max_value=datetime.now().date(),
            key="start_date"
        )
    with date_col2:
        end_date = st.date_input(
            "End",
            value=datetime.now().date(),
            min_value=start_date,
            key="end_date"
        )

    st.markdown("#### 🏙️ Cities & Centers")
    cities = sorted(set(center['city'] for center in CENTERS))
    selected_cities = st.multiselect(
        "Select Cities",
        options=cities,
        default=cities,
        help="Filter centers by city"
    )
    center_names = [center['centerName'] for center in CENTERS if center['city'] in selected_cities]
    selected_centers = st.multiselect(
        "Select Centers",
        options=center_names,
        default=center_names,
        help="Choose which centers to analyze"
    )

    st.markdown(
        f"<div style='margin-top:10px; font-size:12px; color:#666;'>"
        f"<b>Selected:</b> {len(selected_centers)} centers in {len(selected_cities)} cities"
        f"</div>",
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

access_token = ACCESS_TOKEN

if not selected_centers:
    st.warning("Please select at least one center to analyze.")
    st.stop()

# Route to page modules
if page == "Performance Overview":
    performance_overview.show(selected_centers, start_date, end_date, access_token)
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
elif page == "Meta Ads Metrics":
    meta_metrics.show(selected_centers, start_date, end_date, access_token)

st.markdown("---")
st.markdown("© Sbitis Media 2025")