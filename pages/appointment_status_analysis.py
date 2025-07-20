import streamlit as st
import pandas as pd
from api_client import fetch_appointments_for_centers
import plotly.graph_objects as go

def show(selected_centers, start_date, end_date):
    with st.spinner("Fetching appointment status data..."):
        results = fetch_appointments_for_centers(start_date.isoformat(), end_date.isoformat(), selected_centers)

    valid_results = [r for r in results if 'error' not in r]
    error_results = [r for r in results if 'error' in r]

    if error_results:
        st.error(f"Errors occurred for {len(error_results)} centers:")
        for error in error_results:
            st.error(f"- {error['centerName']}: {error['error']}")

    if not valid_results:
        st.error("No valid appointment data retrieved. Please check your API keys and try again.")
        st.stop()

    st.markdown("---")
    st.markdown("### 📅 Appointment Status Analysis")
    st.markdown(f"**Analysis Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    st.markdown(f"**Centers Analyzed:** {len(valid_results)}")

    summary_rows = []
    for center_data in valid_results:
        center_name = center_data['centerName']
        city = center_data['city']
        totals = center_data.get('totals', {})
        ratios = center_data.get('ratios', {})
        total_appointments = center_data.get('totalAppointments', 0)
        summary_rows.append({
            'Center': center_name,
            'City': city,
            'Total Appointments': total_appointments,
            'Confirmed': totals.get('confirmed', 0),
            'Cancelled': totals.get('cancelled', 0),
            'No Show': totals.get('noshow', 0),
            'Showed Up': totals.get('showed', 0),
            'New': totals.get('new', 0),
            'Invalid': totals.get('invalid', 0),
            'Confirmation Rate (%)': f"{ratios.get('confirmationRate', 0):.2f}",
            'Cancellation Rate (%)': f"{ratios.get('cancellationRate', 0):.2f}",
            'No Show Rate (%)': f"{ratios.get('noShowRate', 0):.2f}",
            'Show Up Rate (%)': f"{ratios.get('showUpRate', 0):.2f}"
        })

    df_summary = pd.DataFrame(summary_rows)

    # 📋 Detailed Summary by Center
    st.subheader("📋 Detailed Summary by Center")
    st.dataframe(df_summary, use_container_width=True)

    # 🏆 Center Ratios Overview with color coding
    ratios_table = df_summary[[
        'Center',
        'Confirmation Rate (%)',
        'Show Up Rate (%)',
        'Cancellation Rate (%)',
        'No Show Rate (%)'
    ]].copy()

    def color_ratio(val, col):
        try:
            val = float(val)
        except Exception:
            return ''
        
        if col == 'Confirmation Rate (%)':
            # 🟢 >60% | 🟡 40-60% | 🔴 <40%
            if val > 60:
                return 'background-color: #d4edda; color: #155724'  # Green
            elif val >= 40:
                return 'background-color: #fff3cd; color: #856404'  # Yellow
            else:
                return 'background-color: #f8d7da; color: #721c24'  # Red
        
        elif col == 'Show Up Rate (%)':
            # 🟢 >50% | 🟡 35-50% | 🔴 <35%
            if val > 50:
                return 'background-color: #d4edda; color: #155724'  # Green
            elif val >= 35:
                return 'background-color: #fff3cd; color: #856404'  # Yellow
            else:
                return 'background-color: #f8d7da; color: #721c24'  # Red
        
        elif col == 'Cancellation Rate (%)':
            # 🟢 <30% | 🟡 30-40% | 🔴 >40%
            if val < 30:
                return 'background-color: #d4edda; color: #155724'  # Green
            elif val <= 40:
                return 'background-color: #fff3cd; color: #856404'  # Yellow
            else:
                return 'background-color: #f8d7da; color: #721c24'  # Red
        
        elif col == 'No Show Rate (%)':
            # 🟢 <30% | 🟡 30-40% | 🔴 >40%
            if val < 30:
                return 'background-color: #d4edda; color: #155724'  # Green
            elif val <= 40:
                return 'background-color: #fff3cd; color: #856404'  # Yellow
            else:
                return 'background-color: #f8d7da; color: #721c24'  # Red
        
        return ''

    styled_ratios = ratios_table.style.apply(
        lambda row: [color_ratio(val, col) if col != 'Center' else '' for val, col in zip(row, row.index)],
        axis=1
    )

    st.subheader("🏆 Center Ratios Overview")
    st.dataframe(styled_ratios, use_container_width=True)