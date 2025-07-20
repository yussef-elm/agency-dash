"""
Meta Ads Metrics Dashboard
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from api_client import fetch_meta_metrics_for_centers

def format_currency(value):
    return f"${value:,.2f}"

def format_percentage(value):
    return f"{value:.2f}%"

def create_all_centers_table(df):
    """Show all centers in a single sortable/filterable table"""
    st.subheader("📋 All Centers Meta Ads Metrics")
    display_df = df.copy()
    display_df['Spend'] = display_df['Spend'].apply(format_currency)
    display_df['CPM'] = display_df['CPM'].apply(format_currency)
    display_df['CTR'] = display_df['CTR'].apply(format_percentage)
    display_df['CPR'] = display_df['CPR'].apply(format_currency)
    st.dataframe(display_df, use_container_width=True)

def create_metrics_cards(df):
    total_leads = df['Leads'].sum()
    total_spend = df['Spend'].sum()
    avg_cpm = df['CPM'].mean()
    avg_ctr = df['CTR'].mean()
    avg_cpr = df['CPR'].mean()
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("🎯 Total Leads", f"{total_leads:,}")
    with col2:
        st.metric("💰 Total Spend", format_currency(total_spend))
    with col3:
        st.metric("📊 Avg CPM", format_currency(avg_cpm))
    with col4:
        st.metric("👆 Avg CTR", format_percentage(avg_ctr))
    with col5:
        st.metric("💵 Avg CPR", format_currency(avg_cpr))

def create_city_comparison_chart(df):
    st.subheader("📍 Performance by City (Averages)")
    city_summary = df.groupby('City').agg({
        'CPM': 'mean',
        'CPR': 'mean',
        'CTR': 'mean'
    }).reset_index()
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Avg CPM by City', 'Avg CPR by City', 'Avg CTR by City'),
        specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
    )
    fig.add_trace(
        go.Bar(x=city_summary['City'], y=city_summary['CPM'], name='CPM', marker_color='#2ca02c'),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=city_summary['City'], y=city_summary['CPR'], name='CPR', marker_color='#9467bd'),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(x=city_summary['City'], y=city_summary['CTR'], name='CTR', marker_color='#d62728'),
        row=1, col=3
    )
    fig.update_layout(height=400, showlegend=False, title_text="City Performance (Averages)")
    st.plotly_chart(fig, use_container_width=True)

def create_detailed_tables(df):
    st.subheader("📋 Detailed Metrics by City")
    for city in sorted(df['City'].unique()):
        with st.expander(f"📍 {city} Centers"):
            city_df = df[df['City'] == city].copy()
            display_df = city_df[['Center', 'Leads', 'Spend', 'CPM', 'CTR', 'CPR']].copy()
            display_df['Spend'] = display_df['Spend'].apply(format_currency)
            display_df['CPM'] = display_df['CPM'].apply(format_currency)
            display_df['CTR'] = display_df['CTR'].apply(format_percentage)
            display_df['CPR'] = display_df['CPR'].apply(format_currency)
            st.dataframe(display_df, use_container_width=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Leads", f"{city_df['Leads'].sum():,}")
            with col2:
                st.metric("Total Spend", format_currency(city_df['Spend'].sum()))
            with col3:
                st.metric("Avg CPR", format_currency(city_df['CPR'].mean()))
            with col4:
                st.metric("Avg CTR", format_percentage(city_df['CTR'].mean()))

def show(selected_centers, start_date, end_date, access_token):
    st.title("📊 Meta Ads Performance Dashboard")
    with st.spinner("Fetching Meta Ads data..."):
        try:
            results = fetch_meta_metrics_for_centers(
                start_date.isoformat(), 
                end_date.isoformat(), 
                selected_centers, 
                access_token
            )
        except Exception as e:
            st.error(f"Error fetching Meta Ads data: {str(e)}")
            return
    if not results:
        st.warning("No Meta Ads data available for the selected centers and date range.")
        return
    summary_rows = []
    errors = []
    for center_data in results:
        metrics = center_data['metrics']
        if 'error' in metrics:
            errors.append(f"{center_data['centerName']}: {metrics['error']}")
            continue
        summary_rows.append({
            'Center': center_data['centerName'],
            'City': center_data['city'],
            'Leads': metrics['leads'],
            'Spend': metrics['spend'],
            'CPM': metrics['cpm'],
            'CTR': metrics['ctr'],
            'CPR': metrics['cpr'],
            # Example: add more metrics here if you fetch them from Meta
            # 'Hook Rate': metrics.get('hook_rate', 0.0)
        })
    if errors:
        st.error("Errors occurred for some centers:")
        for error in errors:
            st.error(f"• {error}")
    if not summary_rows:
        st.error("No valid Meta Ads data retrieved.")
        return
    df = pd.DataFrame(summary_rows)
    st.markdown("---")
    st.markdown(f"**📅 Analysis Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    st.markdown(f"**🏢 Centers Analyzed:** {len(df)} centers across {df['City'].nunique()} cities")
    # All centers table
    create_all_centers_table(df)
    st.markdown("---")
    # Overview metrics cards
    create_metrics_cards(df)
    st.markdown("---")
    # City comparison charts (averages only)
    create_city_comparison_chart(df)
    st.markdown("---")
    # Detailed tables by city
    create_detailed_tables(df)
    # Export option
    st.markdown("---")
    st.subheader("📥 Export Data")
    if st.button("Download CSV Report"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Meta Ads Report",
            data=csv,
            file_name=f"meta_ads_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# To add more metrics (like hook rate), update your fetch_meta_metrics function in api_client.py:
# 1. Add the metric to the "fields" param (e.g., "hook_rate").
# 2. Extract it from the API response and include it in the returned dict.
# 3. Add it to the summary_rows dict above and display as needed.