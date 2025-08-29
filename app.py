import streamlit as st
from weather_agent import WeatherAgent
from dotenv import load_dotenv
import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Load API key
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

agent = WeatherAgent(API_KEY)

st.set_page_config(page_title="🌦️ Weather Agent", layout="centered")
st.title("🌍 Auto Weather Forecast App")

# Detect location
def detect_city():
    try:
        res = requests.get("http://ip-api.com/json/").json()
        return res.get("city", "Hyderabad")
    except:
        return "Hyderabad"

# Get weather icon URL
def weather_icon(icon_code):
    return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

# Format date
def format_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")

def format_day(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")

# City
city = detect_city()
st.info(f"Detected Location: **{city}**")

# Data
current_data = agent.get_weather_data(city)
forecast_data = agent.get_forecast_data(city)

if "error" in current_data:
    st.error(f"Current Weather Error ({current_data['error']}): {current_data['message']}")
elif "error" in forecast_data:
    st.error(f"Forecast Error ({forecast_data['error']}): {forecast_data['message']}")
else:
    tabs = st.tabs(["Current Weather", "Hourly Forecast", "Daily Forecast"])

    # Current
    with tabs[0]:
        st.header("🌤️ Current Weather")
        weather = current_data['weather'][0]['description'].title()
        icon = current_data['weather'][0]['icon']
        st.image(weather_icon(icon), width=100)
        st.metric("Temperature", f"{current_data['main']['temp']} °C")
        st.metric("Humidity", f"{current_data['main']['humidity']}%")
        st.metric("Weather", weather)

    # Hourly (next 24h = 8 entries)
    with tabs[1]:
        st.header("🕒 Hourly Forecast (Next 24 Hours)")
        hourly_list = forecast_data.get("list", [])[:8]
        if hourly_list:
            df_hourly = pd.DataFrame([{
                "Time": format_date(item["dt_txt"]),
                "Temp (°C)": item["main"]["temp"],
                "Humidity (%)": item["main"]["humidity"],
                "Weather": item['weather'][0]['description'].title(),
                "Icon": weather_icon(item['weather'][0]['icon'])
            } for item in hourly_list])
            
            # Display rows with icons
            for _, row in df_hourly.iterrows():
                cols = st.columns([2,2,2,2,1])
                cols[0].write(row["Time"])
                cols[1].write(f"{row['Temp (°C)']} °C")
                cols[2].write(f"{row['Humidity (%)']} %")
                cols[3].write(row["Weather"])
                cols[4].image(row["Icon"], width=50)

            # Temperature trend chart
            st.subheader("📈 Hourly Temperature Trend")
            fig, ax = plt.subplots()
            ax.plot(df_hourly["Time"], df_hourly["Temp (°C)"], marker="o")
            ax.set_xlabel("Time")
            ax.set_ylabel("Temperature (°C)")
            ax.tick_params(axis="x", rotation=45)
            st.pyplot(fig)
        else:
            st.warning("No hourly data available.")

    # Daily (next 7 days = pick every 8th entry)
    with tabs[2]:
        st.header("📅 Daily Forecast (Next 7 Days)")
        daily_list = forecast_data.get("list", [])[::8][:7]
        if daily_list:
            df_daily = pd.DataFrame([{
                "Date": format_day(item["dt_txt"]),
                "Temp (°C)": item["main"]["temp"],
                "Humidity (%)": item["main"]["humidity"],
                "Weather": item['weather'][0]['description'].title(),
                "Icon": weather_icon(item['weather'][0]['icon'])
            } for item in daily_list])

            for _, row in df_daily.iterrows():
                cols = st.columns([2,2,2,2,1])
                cols[0].write(row["Date"])
                cols[1].write(f"{row['Temp (°C)']} °C")
                cols[2].write(f"{row['Humidity (%)']} %")
                cols[3].write(row["Weather"])
                cols[4].image(row["Icon"], width=50)

            # Temperature trend chart
            st.subheader("📈 Daily Temperature Trend")
            fig, ax = plt.subplots()
            ax.plot(df_daily["Date"], df_daily["Temp (°C)"], marker="o")
            ax.set_xlabel("Date")
            ax.set_ylabel("Temperature (°C)")
            ax.tick_params(axis="x", rotation=45)
            st.pyplot(fig)
        else:
            st.warning("No daily data available.")
