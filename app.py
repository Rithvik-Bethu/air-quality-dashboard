
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Air Quality Dashboard",
    page_icon="🌍",
    layout="wide"
)

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("data/city_day.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["AQI"] = pd.to_numeric(df["AQI"], errors="coerce")
    return df

df = load_data()

# Dashboard title
st.title("Air Quality and Pollution Analytics")
st.write(
    "Explore historical air quality across Indian cities "
    "from 2015 to 2020."
)

# Sidebar filters
st.sidebar.header("Filters")

cities = sorted(df["City"].dropna().unique())
selected_city = st.sidebar.selectbox(
    "Select a city",
    ["All Cities"] + cities
)

valid_dates = df["Date"].dropna()
start_date = st.sidebar.date_input(
    "Start date",
    value=valid_dates.min().date(),
    min_value=valid_dates.min().date(),
    max_value=valid_dates.max().date()
)

end_date = st.sidebar.date_input(
    "End date",
    value=valid_dates.max().date(),
    min_value=valid_dates.min().date(),
    max_value=valid_dates.max().date()
)

# Apply filters
filtered = df[
    df["Date"].notna()
    & (df["Date"].dt.date >= start_date)
    & (df["Date"].dt.date <= end_date)
].copy()

if selected_city != "All Cities":
    filtered = filtered[filtered["City"] == selected_city]

# Keep valid AQI records for AQI analysis
aqi_data = filtered.dropna(subset=["AQI"]).copy()

# KPI cards
st.subheader("Air Quality Summary")

col1, col2, col3, col4 = st.columns(4)

if not aqi_data.empty:
    col1.metric("Average AQI", f"{aqi_data['AQI'].mean():.1f}")
    col2.metric("Maximum AQI", f"{aqi_data['AQI'].max():.0f}")
    col3.metric("Minimum AQI", f"{aqi_data['AQI'].min():.0f}")
    col4.metric("Valid AQI Records", f"{len(aqi_data):,}")
else:
    st.warning("No valid AQI measurements match these filters.")

# AQI trend
st.subheader("AQI Trend Over Time")

if not aqi_data.empty:
    daily_aqi = (
        aqi_data.groupby("Date", as_index=False)["AQI"]
        .mean()
        .sort_values("Date")
    )

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(daily_aqi["Date"], daily_aqi["AQI"])
    ax.set_xlabel("Date")
    ax.set_ylabel("Average AQI")
    ax.set_title("Daily Average AQI")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# City comparison
st.subheader("Average AQI by City")

if not filtered.dropna(subset=["AQI"]).empty:
    city_aqi = (
        filtered.groupby("City")["AQI"]
        .mean()
        .dropna()
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    city_aqi.plot(kind="barh", ax=ax)
    ax.set_xlabel("Average AQI")
    ax.set_ylabel("City")
    ax.set_title("City-wise Average AQI")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# Data preview
st.subheader("Filtered Dataset Preview")
st.dataframe(filtered.head(100), use_container_width=True)

st.caption(
    "Source: downloaded historical India air-quality dataset. "
    "Charts use available observations; missing AQI values are excluded "
    "from AQI calculations."
)