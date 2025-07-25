"""
Enhanced Meta Ads Metrics Dashboard with Guaranteed Metrics Display
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from api_client import fetch_meta_metrics_for_centers

def format_currency(value):
    """Format value as currency"""
    try:
        return f"€{float(value):,.2f}"
    except (ValueError, TypeError):
        return "€0.00"

def format_percentage(value):
    """Format value as percentage"""
    try:
        return f"{float(value):.2f}%"
    except (ValueError, TypeError):
        return "0.00%"

def format_number(value):
    """Format value as number with commas"""
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return "0"

def ensure_all_columns(df):
    """Ensure all expected columns exist in the DataFrame"""
    expected_columns = {
        'Center': '',
        'City': '',
        'Impressions': 0,
        'Link Clicks': 0,
        'Video 30s Views': 0,
        'Leads': 0,
        'Hook Rate': 0.0,
        'Meta Conv. Rate': 0.0,
        'CTR': 0.0,
        'Spend': 0.0,
        'CPM': 0.0,
        'CPR': 0.0
    }

    for col, default_value in expected_columns.items():
        if col not in df.columns:
            df[col] = default_value

    return df

def create_all_centers_table(df):
    """Show all centers in a single sortable/filterable table with enhanced metrics"""
    st.subheader("📋 Complete Meta Ads Metrics - All Centers")

    # Ensure all columns exist
    df = ensure_all_columns(df)

    # Debug info (remove in production)
    st.write("🔍 **Debug Info:**")
    st.write(f"DataFrame shape: {df.shape}")
    st.write(f"Columns: {list(df.columns)}")

    # Create display copy
    display_df = df.copy()

    # Format columns for display (only in display_df)
    display_df['Spend'] = display_df['Spend'].apply(format_currency)
    display_df['CPM'] = display_df['CPM'].apply(format_currency)
    display_df['CPR'] = display_df['CPR'].apply(format_currency)
    display_df['CTR'] = display_df['CTR'].apply(format_percentage)
    display_df['Hook Rate'] = display_df['Hook Rate'].apply(format_percentage)
    display_df['Meta Conv. Rate'] = display_df['Meta Conv. Rate'].apply(format_percentage)
    display_df['Impressions'] = display_df['Impressions'].apply(format_number)
    display_df['Link Clicks'] = display_df['Link Clicks'].apply(format_number)
    display_df['Video 30s Views'] = display_df['Video 30s Views'].apply(format_number)

    # Reorder columns for better readability
    column_order = [
        'Center', 'City', 'Impressions', 'Link Clicks', 'Video 30s Views', 'Leads',
        'Hook Rate', 'Meta Conv. Rate', 'CTR', 'Spend', 'CPM', 'CPR'
    ]

    # Ensure all columns in order exist
    available_columns = [col for col in column_order if col in display_df.columns]
    display_df = display_df[available_columns]

    st.dataframe(
        display_df, 
        use_container_width=True,
        height=400
    )

def create_enhanced_metrics_cards(df):
    """Enhanced metrics cards with new KPIs"""
    # Ensure all columns exist
    df = ensure_all_columns(df)

    # Calculate totals and averages (using numeric df)
    total_leads = df['Leads'].sum()
    total_spend = df['Spend'].sum()
    total_impressions = df['Impressions'].sum()
    total_clicks = df['Link Clicks'].sum()
    total_video_30s = df['Video 30s Views'].sum()

    # Calculate averages safely
    avg_cpm = df['CPM'].mean() if len(df) > 0 else 0
    avg_ctr = df['CTR'].mean() if len(df) > 0 else 0
    avg_cpr = df['CPR'].mean() if len(df) > 0 else 0
    avg_hook_rate = df['Hook Rate'].mean() if len(df) > 0 else 0
    avg_meta_conv_rate = df['Meta Conv. Rate'].mean() if len(df) > 0 else 0

    # Overall rates
    overall_hook_rate = (total_video_30s / total_impressions * 100) if total_impressions > 0 else 0
    overall_meta_conv_rate = (total_leads / total_clicks * 100) if total_clicks > 0 else 0
    overall_cpl = total_spend / total_leads if total_leads > 0 else 0

    st.subheader("📊 Performance Overview")

    # First row - Volume metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("👁️ Total Impressions", format_number(total_impressions))
    with col2:
        st.metric("👆 Total Clicks", format_number(total_clicks))
    with col3:
        st.metric("📺 Video 30s Views", format_number(total_video_30s))
    with col4:
        st.metric("🎯 Total Leads", format_number(total_leads))
    with col5:
        st.metric("💰 Total Spend", format_currency(total_spend))

    # Second row - Rate metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("🪝 Overall Hook Rate", format_percentage(overall_hook_rate))
    with col2:
        st.metric("📈 Overall Meta Conv.", format_percentage(overall_meta_conv_rate))
    with col3:
        st.metric("👆 Avg CTR", format_percentage(avg_ctr))
    with col4:
        st.metric("💵 Overall CPL", format_currency(overall_cpl))
    with col5:
        st.metric("📊 Avg CPM", format_currency(avg_cpm))

def create_enhanced_city_comparison_chart(df):
    """Enhanced city comparison with new metrics"""
    st.subheader("📍 Performance by City")

    # Ensure all columns exist
    df = ensure_all_columns(df)

    # Group by city (using numeric df)
    city_summary = df.groupby('City').agg({
        'CPM': 'mean',
        'CPR': 'mean',
        'CTR': 'mean',
        'Hook Rate': 'mean',
        'Meta Conv. Rate': 'mean',
        'Impressions': 'sum',
        'Link Clicks': 'sum',
        'Video 30s Views': 'sum',
        'Leads': 'sum',
        'Spend': 'sum'
    }).reset_index()

    # Calculate overall rates per city
    city_summary['Overall Hook Rate'] = (city_summary['Video 30s Views'] / city_summary['Impressions'] * 100).fillna(0)
    city_summary['Overall Meta Conv Rate'] = (city_summary['Leads'] / city_summary['Link Clicks'] * 100).fillna(0)
    city_summary['CPL'] = (city_summary['Spend'] / city_summary['Leads']).fillna(0)

    # Create tabs for different chart views
    tab1, tab2, tab3 = st.tabs(["📊 Cost Metrics", "📈 Conversion Rates", "📺 Engagement Metrics"])

    with tab1:
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('CPM by City', 'CPR by City', 'CPL by City'),
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
            go.Bar(x=city_summary['City'], y=city_summary['CPL'], name='CPL', marker_color='#ff7f0e'),
            row=1, col=3
        )

        fig.update_layout(height=400, showlegend=False, title_text="Cost Metrics by City")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('CTR by City', 'Hook Rate by City', 'Meta Conv. Rate by City'),
            specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
        )

        fig.add_trace(
            go.Bar(x=city_summary['City'], y=city_summary['CTR'], name='CTR', marker_color='#d62728'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=city_summary['City'], y=city_summary['Overall Hook Rate'], name='Hook Rate', marker_color='#17becf'),
            row=1, col=2
        )
        fig.add_trace(
            go.Bar(x=city_summary['City'], y=city_summary['Overall Meta Conv Rate'], name='Meta Conv Rate', marker_color='#bcbd22'),
            row=1, col=3
        )

        fig.update_layout(height=400, showlegend=False, title_text="Conversion Rates by City")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Total Impressions', 'Total Clicks', 'Total Video 30s Views'),
            specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
        )

        fig.add_trace(
            go.Bar(x=city_summary['City'], y=city_summary['Impressions'], name='Impressions', marker_color='#1f77b4'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=city_summary['City'], y=city_summary['Link Clicks'], name='Clicks', marker_color='#ff7f0e'),
            row=1, col=2
        )
        fig.add_trace(
            go.Bar(x=city_summary['City'], y=city_summary['Video 30s Views'], name='Video Views', marker_color='#2ca02c'),
            row=1, col=3
        )

        fig.update_layout(height=400, showlegend=False, title_text="Engagement Volume by City")
        st.plotly_chart(fig, use_container_width=True)

def create_performance_insights(df):
    """Create performance insights section"""
    st.subheader("💡 Performance Insights")

    # Ensure all columns exist
    df = ensure_all_columns(df)

    if len(df) >= 2:
        # Find best performers (using numeric df)
        best_hook_rate = df.loc[df['Hook Rate'].idxmax()]
        best_meta_conv = df.loc[df['Meta Conv. Rate'].idxmax()]
        best_ctr = df.loc[df['CTR'].idxmax()]

        # Find most efficient (lowest costs)
        best_cpm = df.loc[df['CPM'].idxmin()]
        best_cpr = df.loc[df['CPR'].idxmin()]

        # Calculate CPL for best performer
        df_with_cpl = df.copy()
        df_with_cpl['CPL'] = df_with_cpl['Spend'] / df_with_cpl['Leads']
        df_with_cpl = df_with_cpl[df_with_cpl['CPL'] != float('inf')]  # Remove infinite values

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🏆 Top Performers")
            st.success(f"🪝 **Best Hook Rate**: {best_hook_rate['Center']} ({best_hook_rate['Hook Rate']:.2f}%)")
            st.success(f"📈 **Best Meta Conv. Rate**: {best_meta_conv['Center']} ({best_meta_conv['Meta Conv. Rate']:.2f}%)")
            st.success(f"👆 **Best CTR**: {best_ctr['Center']} ({best_ctr['CTR']:.2f}%)")

        with col2:
            st.markdown("#### 💰 Most Cost-Efficient")
            st.info(f"📊 **Lowest CPM**: {best_cpm['Center']} (€{best_cpm['CPM']:.2f})")
            st.info(f"💵 **Lowest CPR**: {best_cpr['Center']} (€{best_cpr['CPR']:.2f})")
            if len(df_with_cpl) > 0:
                best_cpl = df_with_cpl.loc[df_with_cpl['CPL'].idxmin()]
                st.info(f"🎯 **Lowest CPL**: {best_cpl['Center']} (€{best_cpl['CPL']:.2f})")
    else:
        st.info("Need at least 2 centers to show performance insights.")

def create_detailed_tables(df):
    """Enhanced detailed tables by city with new metrics"""
    st.subheader("📋 Detailed Metrics by City")

    # Ensure all columns exist
    df = ensure_all_columns(df)

    for city in sorted(df['City'].unique()):
        with st.expander(f"📍 {city} Centers", expanded=False):
            city_df = df[df['City'] == city].copy()

            # Create display dataframe with formatted values
            display_columns = [
                'Center', 'Impressions', 'Link Clicks', 'Video 30s Views', 'Leads',
                'Hook Rate', 'Meta Conv. Rate', 'CTR', 'Spend', 'CPM', 'CPR'
            ]

            # Ensure all display columns exist
            for col in display_columns:
                if col not in city_df.columns:
                    city_df[col] = 0 if col != 'Center' else ''

            display_df = city_df[display_columns].copy()

            # Format for display
            display_df['Impressions'] = display_df['Impressions'].apply(format_number)
            display_df['Link Clicks'] = display_df['Link Clicks'].apply(format_number)
            display_df['Video 30s Views'] = display_df['Video 30s Views'].apply(format_number)
            display_df['Hook Rate'] = display_df['Hook Rate'].apply(format_percentage)
            display_df['Meta Conv. Rate'] = display_df['Meta Conv. Rate'].apply(format_percentage)
            display_df['CTR'] = display_df['CTR'].apply(format_percentage)
            display_df['Spend'] = display_df['Spend'].apply(format_currency)
            display_df['CPM'] = display_df['CPM'].apply(format_currency)
            display_df['CPR'] = display_df['CPR'].apply(format_currency)

            st.dataframe(display_df, use_container_width=True)

            # City summary metrics (using numeric city_df)
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Total Impressions", format_number(city_df['Impressions'].sum()))
            with col2:
                st.metric("Total Leads", format_number(city_df['Leads'].sum()))
            with col3:
                st.metric("Total Spend", format_currency(city_df['Spend'].sum()))
            with col4:
                avg_hook = city_df['Hook Rate'].mean()
                st.metric("Avg Hook Rate", format_percentage(avg_hook))
            with col5:
                avg_meta_conv = city_df['Meta Conv. Rate'].mean()
                st.metric("Avg Meta Conv.", format_percentage(avg_meta_conv))

def show(selected_centers, start_date, end_date, access_token):
    st.title("📊 Enhanced Meta Ads Performance Dashboard")

    if not access_token:
        st.error("🔑 Meta Ads access token is required to view this dashboard.")
        st.info("Please configure your Meta Ads access token in the app settings.")
        return

    with st.spinner("Fetching enhanced Meta Ads data..."):
        try:
            results = fetch_meta_metrics_for_centers(
                start_date.isoformat(), 
                end_date.isoformat(), 
                selected_centers, 
                access_token
            )
        except Exception as e:
            st.error(f"Error fetching Meta Ads data: {str(e)}")
            with st.expander("🔧 Technical Details"):
                st.code(str(e))
            return

    if not results:
        st.warning("No Meta Ads data available for the selected centers and date range.")
        return

    # Process results with enhanced metrics
    summary_rows = []
    errors = []

    for center_data in results:
        metrics = center_data['metrics']

        if 'error' in metrics:
            errors.append(f"{center_data['centerName']}: {metrics['error']}")
            continue

        # Ensure all metrics are present with defaults
        summary_rows.append({
            'Center': center_data['centerName'],
            'City': center_data['city'],
            'Leads': metrics.get('leads', 0),
            'Spend': metrics.get('spend', 0.0),
            'CPM': metrics.get('cpm', 0.0),
            'CTR': metrics.get('ctr', 0.0),
            'CPR': metrics.get('cpr', 0.0),
            # Enhanced metrics with guaranteed defaults
            'Impressions': metrics.get('impressions', 0),
            'Link Clicks': metrics.get('inline_link_clicks', 0),
            'Video 30s Views': metrics.get('video_30_sec_watched', 0),
            'Hook Rate': metrics.get('hook_rate', 0.0),
            'Meta Conv. Rate': metrics.get('conversion_rate', 0.0)
        })

    # Show errors if any
    if errors:
        with st.expander(f"⚠️ {len(errors)} centers have data issues", expanded=False):
            for error in errors:
                st.error(f"• {error}")

    if not summary_rows:
        st.error("No valid Meta Ads data retrieved.")
        return

    # Create DataFrame
    df = pd.DataFrame(summary_rows)

    # Ensure all columns exist
    df = ensure_all_columns(df)

    # Header information
    st.markdown("---")
    st.markdown(f"**📅 Analysis Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    st.markdown(f"**🏢 Centers Analyzed:** {len(df)} centers across {df['City'].nunique()} cities")

    # Enhanced metrics cards
    create_enhanced_metrics_cards(df)

    st.markdown("---")

    # All centers table with enhanced metrics
    create_all_centers_table(df)

    st.markdown("---")

    # Performance insights
    create_performance_insights(df)

    st.markdown("---")

    # Enhanced city comparison charts
    create_enhanced_city_comparison_chart(df)

    st.markdown("---")

    # Detailed tables by city
    create_detailed_tables(df)

    # Enhanced export options
    st.markdown("---")
    st.subheader("📥 Export Enhanced Data")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Complete dataset (use numeric df for export)
        csv_complete = df.to_csv(index=False)
        st.download_button(
            label="📄 Download Complete Report (CSV)",
            data=csv_complete,
            file_name=f"meta_ads_complete_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    with col2:
        # Cost-focused data
        cost_columns = ['Center', 'City', 'Spend', 'CPM', 'CPR', 'Leads']
        available_cost_columns = [col for col in cost_columns if col in df.columns]
        cost_df = df[available_cost_columns]
        cost_csv = cost_df.to_csv(index=False)
        st.download_button(
            label="💰 Download Cost Metrics (CSV)",
            data=cost_csv,
            file_name=f"meta_ads_costs_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    with col3:
        # Engagement-focused data
        engagement_columns = ['Center', 'City', 'Impressions', 'Link Clicks', 'Video 30s Views', 'Hook Rate', 'Meta Conv. Rate', 'CTR']
        available_engagement_columns = [col for col in engagement_columns if col in df.columns]
        engagement_df = df[available_engagement_columns]
        engagement_csv = engagement_df.to_csv(index=False)
        st.download_button(
            label="📈 Download Engagement Metrics (CSV)",
            data=engagement_csv,
            file_name=f"meta_ads_engagement_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    # Summary statistics
    with st.expander("📊 Summary Statistics", expanded=False):
        st.markdown("#### 📈 Overall Performance")

        # Use numeric df for calculations
        total_impressions = df['Impressions'].sum()
        total_clicks = df['Link Clicks'].sum()
        total_video_30s = df['Video 30s Views'].sum()
        total_leads = df['Leads'].sum()
        total_spend = df['Spend'].sum()

        overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        overall_hook_rate = (total_video_30s / total_impressions * 100) if total_impressions > 0 else 0
        overall_conv_rate = (total_leads / total_clicks * 100) if total_clicks > 0 else 0
        overall_cpl = total_spend / total_leads if total_leads > 0 else 0

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Total Campaign Reach:** {total_impressions:,} impressions")
            st.markdown(f"**Total Engagement:** {total_clicks:,} clicks")
            st.markdown(f"**Total Video Engagement:** {total_video_30s:,} 30s views")
            st.markdown(f"**Total Leads Generated:** {total_leads:,}")

        with col2:
            st.markdown(f"**Overall CTR:** {overall_ctr:.2f}%")
            st.markdown(f"**Overall Hook Rate:** {overall_hook_rate:.2f}%")
            st.markdown(f"**Overall Conversion Rate:** {overall_conv_rate:.2f}%")
            st.markdown(f"**Overall CPL:** €{overall_cpl:.2f}")

    # Show raw JSON response for debugging / transparency
    st.markdown("---")
    st.subheader("🗂️ Raw Meta Ads JSON Data (for debugging)")
    st.expander("Show raw JSON data", expanded=False).json(results)