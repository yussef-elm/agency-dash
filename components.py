"""
UI components for the dashboard including colored tables
"""
import streamlit as st
import pandas as pd
from utils import get_color_class, create_metric_card

def create_colored_dataframe(df, metric_columns):
    """Create a dataframe with colored cells based on performance"""

    def color_cells(val, column_name):
        """Apply color styling to cells"""
        if column_name in metric_columns:
            metric_type = metric_columns[column_name]
            color_class = get_color_class(val, metric_type)

            if color_class == 'cell-green':
                return 'background-color: #d4edda; color: #155724; font-weight: bold'
            elif color_class == 'cell-yellow':
                return 'background-color: #fff3cd; color: #856404; font-weight: bold'
            elif color_class == 'cell-red':
                return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
            else:
                return 'background-color: #f8f9fa; color: #495057'
        return ''

    styled_df = df.style

    for col in df.columns:
        if col in metric_columns:
            styled_df = styled_df.applymap(
                lambda x: color_cells(x, col), 
                subset=[col]
            )

    return styled_df

def display_benchmark_legend():
    st.markdown("""
    <div style="
        background: linear-gradient(90deg, #f8f9fa, #e9ecef);
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 8px 12px;
        margin: 8px 0;
        font-size: 13px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        white-space: nowrap;
        overflow-x: auto;
    ">
        <span style="font-weight: 600; color: #2c3e50;">📊 Benchmarks:</span>
        <span style="margin: 0 12px; color: #636e72;">Confirmation: <span style="color: #00b894;">🟢>60%</span> <span style="color: #fdcb6e;">🟡40-60%</span> <span style="color: #e17055;">🔴<40%</span></span>
        <span style="margin: 0 12px; color: #636e72;">Show Up: <span style="color: #00b894;">🟢>50%</span> <span style="color: #fdcb6e;">🟡35-50%</span> <span style="color: #e17055;">🔴<35%</span></span>
        <span style="margin: 0 12px; color: #636e72;">Conversion: <span style="color: #00b894;">🟢>50%</span> <span style="color: #fdcb6e;">🟡30-50%</span> <span style="color: #e17055;">🔴<30%</span></span>
        <span style="color: #636e72;">Cancellation: <span style="color: #00b894;">🟢<30%</span> <span style="color: #fdcb6e;">🟡30-40%</span> <span style="color: #e17055;">🔴>40%</span></span>
    </div>
    """, unsafe_allow_html=True)
    
def display_kpi_cards(valid_results):
    """Display KPI cards with color coding"""
    total_rdv = sum([r['metrics']['totalRDVPlanifies'] for r in valid_results])
    total_confirmed = sum([r['metrics']['rdvConfirmes'] for r in valid_results])
    total_showup = sum([r['metrics']['showUp'] for r in valid_results])
    avg_confirmation = (total_confirmed / total_rdv * 100) if total_rdv > 0 else 0
    avg_conversion = (total_showup / total_confirmed * 100) if total_confirmed > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_card("Total RDV", f"{total_rdv:,}", "volume"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Confirmed", f"{total_confirmed:,}", "volume"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Show Up", f"{total_showup:,}", "volume"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("Avg Conversion", f"{avg_conversion:.1f}%", "conversion"), unsafe_allow_html=True)

def display_detailed_metrics_table(valid_results):
    """Display detailed metrics table with color coding"""
    detailed_data = []
    for r in valid_results:
        row = {
            "Center": r['centerName'],
            "City": r['city'],
            "Total RDV": r['metrics']['totalRDVPlanifies'],
            "Confirmed": r['metrics']['rdvConfirmes'],
            "Show Up": r['metrics']['showUp'],
            "Confirmation Rate": r['metrics']['tauxConfirmation'],
            "Cancellation Rate": r['metrics']['tauxAnnulation'],
            "No Show Rate": r['metrics']['tauxNoShow'],
            "Presence Rate": r['metrics']['tauxPresence'],
            "Conversion Rate": r['metrics']['tauxConversion'],
            "Annulé": r['metrics']['details']['annule'],
            "Confirmé": r['metrics']['details']['confirme'],
            "Pas Venu": r['metrics']['details']['pasVenu'],
            "Présent": r['metrics']['details']['present'],
            "Concrétisé": r['metrics']['details']['concretise'],
            "Non Confirmé": r['metrics']['details']['nonConfirme']
        }
        detailed_data.append(row)

    df = pd.DataFrame(detailed_data)

    metric_columns = {
        "Confirmation Rate": "confirmation",
        "Cancellation Rate": "cancellation", 
        "No Show Rate": "no_answer",
        "Presence Rate": "show_up",
        "Conversion Rate": "conversion"
    }

    styled_df = create_colored_dataframe(df, metric_columns)

    st.dataframe(styled_df, use_container_width=True)

    return df

def display_benchmark_analysis_cards(valid_results):
    """Display benchmark analysis with colored cards for each center"""
    for r in valid_results:
        st.subheader(f"🏢 {r['centerName']} - {r['city']}")

        col1, col2, col3, col4, col5 = st.columns(5)
        metrics = r['metrics']

        with col1:
            st.markdown(create_metric_card("Confirmation", metrics['tauxConfirmation'], "confirmation"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card("Show Up", metrics['tauxPresence'], "show_up"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card("Conversion", metrics['tauxConversion'], "conversion"), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card("Cancellation", metrics['tauxAnnulation'], "cancellation"), unsafe_allow_html=True)
        with col5:
            st.markdown(create_metric_card("No Show", metrics['tauxNoShow'], "no-show"), unsafe_allow_html=True)

def display_stage_analysis_table(valid_results):
    """Display stage analysis table with color coding"""
    all_stages = set()
    for r in valid_results:
        if 'stageStats' in r:
            all_stages.update(r['stageStats'].keys())

    stage_data = []
    for r in valid_results:
        row = {
            "Center": r['centerName'],
            "City": r['city'],
            "Total RDV": r['metrics']['totalRDVPlanifies']
        }
        for stage in sorted(all_stages):
            row[stage] = r.get('stageStats', {}).get(stage, 0)
        stage_data.append(row)

    if stage_data:
        stage_df = pd.DataFrame(stage_data)
        st.dataframe(stage_df, use_container_width=True)
        return stage_df
    return None