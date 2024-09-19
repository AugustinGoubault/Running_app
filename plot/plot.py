import pandas as pd
import plotly.graph_objects as go
import datetime as dt

from src.data_processing import data_transform as dtf
from utils import COLORS, WEEKDAY

c_dtf = dtf.DataTransform()


    
def plot_evolution_distance(fig, x_data, y_data)-> go.Figure:
    '''plot evolution of distance and time over the year'''
    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        mode='lines+markers',
        line=dict(color=COLORS[0]),
        name='distance',
        fill="tozeroy",
        fillcolor=COLORS[2],
        hovertemplate="Week: %{x}<br>Distance: %{y:.2f} km")
        )
    return fig

def plot_bar_chart_monthly_distance(fig, x_data, y_data)-> go.Figure:
    '''plot bar chart with monthly distance'''
    fig.add_trace(go.Bar(
        x=x_data,
        y=y_data,
        width=1e9,
        marker=dict(color=COLORS[2],
                    line=dict(color=COLORS[0], width=1)),
        name='distance',
        hovertemplate="Month: %{x|%b %Y}<br>Distance: %{y:.2f} km",
        text=round(y_data),
        texttemplate='<b>%{text} km</b>',  # Format text to be bold
        textposition='outside',  # Position text outside the bar)
        textfont=dict(size=15, color="black"),
        )
    )
    return fig

def add_average_distance_line(fig, y_data)-> go.Figure:
    '''add average line to the plot'''
    fig.add_hline(
        y=y_data.mean(),
        line=dict(color=COLORS[1], width=2, dash="dash"),
        annotation=dict(text=f"Average: {y_data.mean():.2f} km", x=0.2)
    )
    return fig


def update_fig_layout(fig:go.Figure)-> go.Figure:
    fig.update_layout(
        plot_bgcolor="white",
        width=1000,
        height=600,
        font=dict(size=16, color="black"),
    )
    fig.update_yaxes(
        mirror=True,
        linecolor='black',
        showgrid=True,
        gridcolor='lightgrey',
        zeroline=True,
        zerolinecolor='lightgrey',
        zerolinewidth=1,
        ticks="outside",
        tickfont=dict(size=15, color="black"),
    )

    fig.update_xaxes(
        mirror=True,
        linecolor='black',
        showgrid=True,
        gridcolor='lightgrey',
        zeroline=True,
        zerolinecolor='lightgrey',
        zerolinewidth=1,
        ticks="outside",
        tickfont=dict(size=15, color="black"),        
    )
    return fig

def update_weekly_plot(fig:go.Figure, title:str, time_horizon:int)-> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0.5),
    )
    fig.update_xaxes(
        range=[c_dtf.get_first_day_of_period(week_delta=4*time_horizon), c_dtf.get_first_day_of_period()]
    )
    fig.update_yaxes(
        ticksuffix=' km'
    )
    return fig

def update_monthly_bar_chart(fig:go.Figure, title:str, time_horizon:int)-> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0.5),
        font=dict(size=15, color="black"),
    )
    fig.update_xaxes(
        range=[c_dtf.get_first_day_of_period(month_delta=time_horizon), c_dtf.get_first_day_of_period()]
    )
    fig.update_yaxes(
        ticksuffix=' km'
    )
    return fig

def update_calendar_plot(fig:go.Figure, title:str, time_horizon:int)-> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0.5),
        font=dict(size=15, color="black"),
    )
    fig.update_xaxes(
        range=[c_dtf.get_first_day_of_period(week_delta=4*time_horizon), c_dtf.get_first_day_of_period()]
    )
    fig.update_yaxes(
        tickvals=list(WEEKDAY.keys()),  # Valeurs numériques originales
        ticktext=[WEEKDAY[val] for val in WEEKDAY.keys()]
    )
    return fig


def plot_bubble_chart_calendar(fig, x_data, y_data, z_data)-> go.Figure:
    '''plot bubble chart with calendar'''
    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        mode='markers',
        marker=dict(
            size=z_data,
            sizemode='area',
            sizeref=2.*max(z_data)/(40**2),
            color=z_data,
            colorscale=[[0, COLORS[3]], [0.5, COLORS[0]], [1, COLORS[4]]],  # Yellow to orange color scale
            cmin=min(z_data),  # Minimum value of the color scale
            cmax=max(z_data),  # Maximum value of the color scale
            colorbar=dict(
                orientation='h',
                y=-0.3,
                len=0.9,
                tickvals=list(range(0, (round(max(z_data)) // 5 + 1) * 5, 5)),
                ticktext=[str(i)+ ' km' for i in range(0, (round(max(z_data)) // 5 + 1) * 5, 5)]),
            line=dict(color=COLORS[1], width=1),
            # opacity=0.7,
        ),
        hovertemplate="Week: %{x}<br>Day: %{y}<br>Distance: %{marker.size:.2f} km"
    ))
    return fig