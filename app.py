import os
import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime as dt
from pathlib import Path

from src.api_methods import get_methods
from src.api_methods import authorize
from src.data_processing import data_transform as dtf
from plot import plot as plt

from utils import GET_ALL_ACTIVITIES_PARAMS, TH, WEEKDAY

st.set_page_config(layout="wide")

c_dtf = dtf.DataTransform()

st.markdown("<h1 style='text-align: center;'>Running performances with Strava data</h1>", unsafe_allow_html=True)
st.divider()


cols_init = st.columns([2, 1, 1, 1, 2])
st.divider()

cols = st.columns([1, 3, 1])


# Home page with authorization link
authorization_url = authorize.get_authorization_url()

code = st.query_params.get("code", None)
if not code:
    cols[1].write('Click the link below to authorize the app and get your data:')
    cols[1].markdown(f"[Authorize with Strava]({authorization_url})")
else:
    code = st.query_params.get("code", None)

    if "acces_token" not in st.session_state:
        access_token = authorize.get_acces_token(code)
        st.session_state["acces_token"] = access_token
    else:
        access_token = st.session_state["acces_token"]

    if access_token:
    
        activities_data = get_methods.access_activity_data(access_token, params=GET_ALL_ACTIVITIES_PARAMS)
        
        activities_data = dtf.preprocess_data(activities_data) # json to dataframe
        activities_data = c_dtf.process_strava_data(activities_data) # clean data
        
        with cols[1]:
            sub_cols = st.columns([1, 1])
            type_activity = sub_cols[0].selectbox('**Select activity type**', activities_data['type'].unique())
            time_horizon = sub_cols[1].selectbox('**Select time horizon**', TH.keys(), index=2)
            time_horizon = TH[time_horizon]


        # Filter data by selected year and activity type
        activities_data_type = c_dtf.mask_df(df=activities_data, column='type', value=type_activity)

        plot_data_week = c_dtf.merge_on_date_start(
            column_name='week_start', 
            freq='W-MON',
            data=c_dtf.groupby_period(
                df=activities_data_type,
                period=['week'])
            ) 

        # metrics for the last week
        cols_init[1].metric(
                    label="**Activities**",
                    value=round(plot_data_week['activity_count'].iloc[-1]),
                    delta=round(plot_data_week['activity_count'].iloc[-1]-plot_data_week['activity_count'].iloc[-2]),
                    delta_color="normal",
                )
        cols_init[2].metric(
            label="**Distance**",
            value=f"{round(plot_data_week['distance'].iloc[-1], 1)} km",
            delta=str(round(plot_data_week['distance'].iloc[-1] - plot_data_week['distance'].iloc[-2], 1)) + " km",
            delta_color="normal",
        )

        time_delta = pd.to_timedelta(plot_data_week['moving_time'].iloc[-1]) - pd.to_timedelta(plot_data_week['moving_time'].iloc[-2])
        time_diff = str(abs(time_delta)).split(" ")[2:][0] if time_delta > pd.Timedelta(0) else "-"+str(abs(time_delta)).split(" ")[2:][0]
        cols_init[3].metric(
            label="**Moving time**",
            value=str(plot_data_week['moving_time'].iloc[-1]).split(" ")[2:][0],
            delta=time_diff,
            delta_color="inverse" if time_delta > pd.Timedelta(0) else "normal",
            
        )

        cols_init[3].write()


        # Different plots for the selected activity type
        # Plot weekly distance over the period
        fig_weekly = go.Figure()
        fig_weekly = plt.plot_evolution_distance(fig=fig_weekly, x_data=plot_data_week['week_start'], y_data=plot_data_week['distance'])
        
        fig_weekly = plt.update_fig_layout(fig=fig_weekly)
        fig_weekly = plt.update_weekly_plot(fig=fig_weekly, title=f"<b>Weekly distance (type: {type_activity}) over the last {time_horizon} months</b>", time_horizon=time_horizon)
        
        cols[1].plotly_chart(fig_weekly, use_container_width=False, theme=None)


        plot_data_month = c_dtf.merge_on_date_start(
            column_name='month_start', 
            freq='MS',
            data=c_dtf.groupby_period(
                df=activities_data_type,
                period=['month'])
            )

        # plot monthly distance over the period
        fig_monthly = go.Figure()
        fig_monthly = plt.plot_bar_chart_monthly_distance(fig=fig_monthly, x_data=plot_data_month['month_start'], y_data=plot_data_month['distance'])
        fig_monthly = plt.update_fig_layout(fig=fig_monthly)
        fig_monthly = plt.update_monthly_bar_chart(fig=fig_monthly, title=f"<b>Monthly distance (type: {type_activity}) over the last {time_horizon} months</b>", time_horizon=time_horizon)

        cols[1].plotly_chart(fig_monthly, use_container_width=False, theme=None)


        plot_data_calendars = c_dtf.merge_on_date_start(
            column_name='week_start', 
            freq='W-MON',
            data=c_dtf.groupby_period(
                df=activities_data_type,
                period=['week', 'day'])
            )

        # plot daily distance over the period
        fig_calendars = go.Figure()
        fig_calendars = plt.plot_bubble_chart_calendar(fig=fig_calendars, x_data=plot_data_calendars['week_start'], y_data=plot_data_calendars['day'], z_data=plot_data_calendars['distance'])
        fig_calendars = plt.update_fig_layout(fig=fig_calendars)
        fig_calendars = plt.update_calendar_plot(fig=fig_calendars, title=f"<b>Daily distance (type: {type_activity}) over the last {time_horizon} months</b>", time_horizon=time_horizon)
        
        cols[1].plotly_chart(fig_calendars, use_container_width=False, theme=None)






