"""
Chart generation functions for the dashboard
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_performance_bar_chart(valid_results):
    df = pd.DataFrame([
        {
            "Center": r['centerName'], 
            "City": r['city'], 
            "RDV": r['metrics']['totalRDVPlanifies'],
            "Confirmation Rate": r['metrics']['confirmationRateNum'],
            "Show Up Rate": r['metrics']['presenceRateNum']
        }
        for r in valid_results
    ])

    fig = px.bar(df, x="Center", y="RDV", color="Confirmation Rate",
                color_continuous_scale=["#dc3545", "#ffc107", "#28a745"],
                title="RDV Volume with Confirmation Rate")
    fig.update_layout(
        xaxis_tickangle=45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='black'
    )
    return fig

def create_performance_radar_chart(valid_results):
    top_centers = sorted(valid_results, key=lambda x: x['metrics']['totalRDVPlanifies'], reverse=True)[:5]

    fig = go.Figure()

    for center in top_centers:
        metrics = center['metrics']
        fig.add_trace(go.Scatterpolar(
            r=[
                metrics['confirmationRateNum'],
                metrics['presenceRateNum'],
                metrics['conversionRateNum'],
                100 - metrics['cancellationRateNum'],
                100 - metrics['noShowRateNum']
            ],
            theta=['Confirmation', 'Presence', 'Conversion', 'Low Cancellation', 'Low No-Show'],
            fill='toself',
            name=center['centerName']
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=True,
        title="Performance Radar (Top 5 Centers)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='black'
    )
    return fig

def create_performance_heatmap(valid_results):
    performance_data = []
    for r in valid_results:
        metrics = r['metrics']
        performance_data.append({
            'Center': r['centerName'],
            'City': r['city'],
            'Confirmation': metrics['confirmationRateNum'],
            'Show Up': metrics['presenceRateNum'],
            'Conversion': metrics['conversionRateNum'],
            'Cancellation': metrics['cancellationRateNum'],
            'No Show': metrics['noShowRateNum']
        })

    df = pd.DataFrame(performance_data)

    fig = px.imshow(
        df.set_index('Center')[['Confirmation', 'Show Up', 'Conversion', 'Cancellation', 'No Show']].T,
        color_continuous_scale=["#dc3545", "#ffc107", "#28a745"],
        aspect="auto",
        title="Performance Heatmap"
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='black'
    )
    return fig

def create_scatter_plot(valid_results):
    df = pd.DataFrame([
        {
            "Center": r['centerName'],
            "City": r['city'],
            "Confirmation Rate": r['metrics']['confirmationRateNum'],
            "Conversion Rate": r['metrics']['conversionRateNum'],
            "RDV Volume": r['metrics']['totalRDVPlanifies']
        }
        for r in valid_results
    ])

    fig = px.scatter(df, x="Confirmation Rate", y="Conversion Rate", 
                    size="RDV Volume", color="City",
                    title="Confirmation vs Conversion Performance",
                    hover_data=["Center"])

    fig.add_hline(y=50, line_dash="dash", line_color="green", annotation_text="Conversion Benchmark (50%)")
    fig.add_vline(x=60, line_dash="dash", line_color="green", annotation_text="Confirmation Benchmark (60%)")

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='black'
    )
    return fig

def create_performance_distribution_chart(valid_results):
    metrics_list = ['confirmationRateNum', 'presenceRateNum', 'conversionRateNum']
    metric_names = ['Confirmation', 'Show Up', 'Conversion']

    fig = go.Figure()

    for i, metric in enumerate(metrics_list):
        values = [r['metrics'][metric] for r in valid_results]
        fig.add_trace(go.Box(y=values, name=metric_names[i]))

    fig.update_layout(
        title="Performance Distribution",
        yaxis_title="Percentage (%)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='black'
    )
    return fig

def create_stage_distribution_chart(stage_totals):
    if stage_totals:
        fig = px.bar(
            x=list(stage_totals.keys()),
            y=list(stage_totals.values()),
            title="Total Opportunities by Stage",
            color=list(stage_totals.values()),
            color_continuous_scale=["#f8f9fa", "#007bff", "#0056b3"]
        )
        fig.update_layout(
            xaxis_tickangle=45,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='black'
        )
        return fig
    return None

def create_city_comparison_charts(city_centers, city):
    charts = {}

    df_rdv = pd.DataFrame([
        {"Center": r['centerName'], "RDV": r['metrics']['totalRDVPlanifies']}
        for r in city_centers
    ])
    fig_rdv = px.bar(df_rdv, x="Center", y="RDV", title=f"RDV in {city}")
    fig_rdv.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='black'
    )
    charts['rdv'] = fig_rdv

    df_showup = pd.DataFrame([
        {"Center": r['centerName'], "Show Up": r['metrics']['showUp']}
        for r in city_centers
    ])
    fig_showup = px.bar(df_showup, x="Center", y="Show Up", title=f"Show Up in {city}")
    fig_showup.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='black'
    )
    charts['showup'] = fig_showup

    return charts


import plotly.express as px
import pandas as pd

def create_appointments_bar_chart(daily_status_counts, centers):
    data = []
    for day, status_dict in daily_status_counts.items():
        for status, center_dict in status_dict.items():
            for center, count in center_dict.items():
                data.append({
                    'Date': day,
                    'Status': status,
                    'Center': center,
                    'Count': count
                })
    df = pd.DataFrame(data)
    if df.empty:
        return None
    fig = px.bar(df, x='Date', y='Count', color='Status', barmode='group',
                 facet_row='Center' if len(centers) > 1 else None,
                 title='Appointments per Day by Status')
    fig.update_layout(xaxis_tickangle=45)
    return fig

def create_appointments_pie_chart(status_totals):
    labels = list(status_totals.keys())
    values = [status_totals[k] for k in labels]
    fig = px.pie(names=labels, values=values, title='Appointment Status Distribution')
    return fig