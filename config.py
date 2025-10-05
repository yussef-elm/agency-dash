import streamlit as st

# Get access token from Streamlit secrets
ACCESS_TOKEN = st.secrets["META_ACCESS_TOKEN"]

# Centers configuration - API keys from Streamlit secrets
CENTERS = [
    {
        "apiKey": st.secrets["WELLNESS_PALACE_API_KEY"],
        "locationId": "1oR9qXdAIvyGyD1LAp8O",
        "city": "Casablanca",
        "centerName": "Wellness Palace",
        "pipelineName": "Nouveau Pipeline",
        "calendarId": "ApPxaeBYILG6C4bkSpc0",
        "businessId": "act_25684814804439146"
    },
    {
        "apiKey": st.secrets["FARES_ESTHETIC_API_KEY"],
        "locationId": "Jg2Kf3oJL5iYKkubmUas",
        "city": "Marrakesh",
        "centerName": "Fares Esthetic Center",
        "pipelineName": "Nouveau Pipeline",
        "calendarId": "GwNJooiGfAn9GjMqphyG",
        "businessId": "act_1656373184910599"
    },
    {
        "apiKey": st.secrets["KINE_CINQ_SENS_API_KEY"],
        "locationId": "WqEplH0DWuSrLBjGOGOk",
        "city": "Rabat",
        "centerName": "Kiné Cinq Sens",
        "pipelineName": "Nouveau Pipeline",
        "calendarId": "w1fw3eqQzkCtt2JN5JJb",
        "businessId": "act_326370360527674"
    },
    {
        "apiKey": st.secrets["DADIJ_API_KEY"],
        "locationId": "ciOKAMMqM7mlx0BccTDf",
        "city": "Rabat",
        "centerName": "Dadij",
        "pipelineName": "DADIJ LEADS PIPELINE",
        "calendarId": "h97fBm4J0I85pYKzLT6e",
        "businessId": "act_3499790706966281"
    },
    {
        "apiKey": st.secrets["CENTRE_PLENITUDE_API_KEY"],
        "locationId": "W7yJkQtKHYciTttbdULr",
        "city": "Marrakesh",
        "centerName": "Centre Plénitude",
        "pipelineName": "Plénitude Pipeline",
        "calendarId": "PSKUglRKRcozvRj9TTjF",
        "businessId": "act_776928644645438"
    },
    {
        "apiKey": st.secrets["CENTRE_KINAISANCE_API_KEY"],
        "locationId": "EdwcJIn4gY869RI4I3NE",
        "city": "Casablanca",
        "centerName": "Centre Kinaisance",
        "pipelineName": "Nouveau Pipeline",
        "calendarId": "4E0AYMcG27owc6ylnRTf",
        "calendarId2": "DHDDTAdMxijNedp0Q8Sk",
        "businessId": "act_701050159071271"
    },
    {
        "apiKey": st.secrets["LE_NEUF_MAROC_API_KEY"],
        "locationId": "a5EZdOGZyuQb8oNjojlk",
        "city": "Casablanca",
        "centerName": "Le Neuf Maroc",
        "pipelineName": "Nouveau Pipeline",
        "calendarId": "dnMc4WakoOzAwYQtT4um",
        "businessId": "act_2508632876144425"
    },
    {
        "apiKey": st.secrets["MAISON_ECLAT_API_KEY"],
        "locationId": "LjG4WZwwm5dQCxiA6Vpf",
        "city": "Larache",
        "centerName": "Maison d'éclat",
        "pipelineName": "Nouveau Pipeline",
        "calendarId": "Yg8rpke3ctiwTF9Cm5RK",
        "businessId": "act_203386272459605"
    },
    {
        "apiKey": st.secrets["CENTRE_BE_SALAM_API_KEY"],
        "locationId": "UL3W2ab5fakmXHeJ9aFd",
        "city": "Casablanca",
        "centerName": "Centre Be Salam",
        "pipelineName": "Nouveau Pipeline",
        "calendarId": "5M1g3Rpl0aAQHbPGf2B5",
        "businessId": "act_3974524579468467"
    },
    {
        "apiKey": st.secrets["KRASOTKA_BEAUTY_API_KEY"],
        "locationId": "bWGWs4ePd1Ma8TT1H33q",
        "city": "Casablanca",
        "centerName": "Krasotka Beauty Center",
        "pipelineName": "Nouveau Pipeline",
        "calendarId": "C82RZoQRjVrjOdBnRvBW",
        "businessId": "act_2166625163851201"
    },
    {
        "apiKey": st.secrets["MAYAE_BEAUTY_API_KEY"],
        "locationId": "MehoIHHbA7tPArx8J9JM",
        "city": "Marrakesh",
        "centerName": "Mayae Beauty Center",
        "pipelineName": "Nouveau Pipeline",
        "calendarId": "HZSSHX1WeZ2juD1vQk0b",
        "businessId": "act_1803648590586295"
    },
    {
        "apiKey": st.secrets["SVEALTHY_API_KEY"],
        "locationId": "ihjnCaPiXntJ1OZwY0B4",
        "city": "Casablanca",
        "centerName": "Svealthy",
        "pipelineName": "Nouveau Pipeline",
        "calendarId": "Fw0K4ezXHzSeOYACb7iq",
        "businessId": "act_513437851427640"
    },
    {
        "apiKey": st.secrets["HERMOSA_API_KEY"],
        "locationId": "CU0oylzxs0owSRY5527f",
        "city": "Laâyoune",
        "centerName": "Hermosa",
        "pipelineName": "Nouveau Pipeline",
        "calendarId": "tCKnA5IyUJ6m4V7kgGFq",
        "businessId": "act_2961653874016169"
    },
        {
        "apiKey": st.secrets["BLOOM_API_KEY"],
        "locationId": "Rz2iTJ7i6YDKDgRE5vxk",
        "city": "Casablanca",
        "centerName": "Bloom Clinic",
        "pipelineName": "Lp Calendar Pipeline",
        "calendarId": "iW0Nuq4XNVu7AOCsDKLF",
        "businessId": "act_1180242759663330"
    }
]

# Benchmark definitions with classic colors
BENCHMARKS = {
    'confirmation': {'excellent': 60, 'good': 40, 'colors': ['#28a745', '#ffc107', '#dc3545']},  # Green, Yellow, Red
    'show_up': {'excellent': 50, 'good': 35, 'colors': ['#28a745', '#ffc107', '#dc3545']},
    'conversion': {'excellent': 50, 'good': 30, 'colors': ['#28a745', '#ffc107', '#dc3545']},
    'cancellation': {'excellent': 30, 'good': 40, 'colors': ['#28a745', '#ffc107', '#dc3545'], 'reverse': True},
    'no_answer': {'excellent': 30, 'good': 40, 'colors': ['#28a745', '#ffc107', '#dc3545'], 'reverse': True}
}

# Color constants
COLORS = {
    'GREEN': '#28a745',
    'YELLOW': '#ffc107', 
    'RED': '#dc3545',
    'NEUTRAL': '#6c757d',
    'PRIMARY': '#007bff',
    'SECONDARY': '#6c757d'
}

# CSS Styling
CUSTOM_CSS = """
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .metric-green { border-left-color: #28a745; }
    .metric-yellow { border-left-color: #ffc107; }
    .metric-red { border-left-color: #dc3545; }
    .metric-neutral { border-left-color: #6c757d; }

    .benchmark-legend {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .benchmark-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 15px;
        margin-top: 15px;
    }

    .benchmark-item {
        background: #f8f9fa;
        padding: 12px;
        border-radius: 8px;
        border-left: 3px solid #007bff;
    }

    /* Table styling for colored cells */
    .colored-table {
        border-collapse: collapse;
        width: 100%;
    }

    .colored-table th, .colored-table td {
        padding: 8px 12px;
        text-align: left;
        border: 1px solid #dee2e6;
    }

    .colored-table th {
        background-color: #f8f9fa;
        font-weight: bold;
    }

    .cell-green {
        background-color: #d4edda !important;
        color: #155724 !important;
        font-weight: bold;
    }

    .cell-yellow {
        background-color: #fff3cd !important;
        color: #856404 !important;
        font-weight: bold;
    }

    .cell-red {
        background-color: #f8d7da !important;
        color: #721c24 !important;
        font-weight: bold;
    }

    .cell-neutral {
        background-color: #f8f9fa !important;
        color: #495057 !important;
    }
</style>
"""
