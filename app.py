import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Road Accident Dashboard", page_icon="🚨", layout="wide"
)

# Header Section
st.title("🚨 Road Accident Survey & Analysis Dashboard")
st.markdown(
    "Yeh dashboard road accident survey data ko analyze aur visualize karne ke liye banaya gaya hai."
)


# Data Load function (Safe Path Handling for .xls / .csv)
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # possible filenames GitHub var asu shaktat
    possible_files = [
        "RTA Dataset.xls",
        "RTA Dataset.csv",
        "RTA_Dataset.csv",
        "RTA_Dataset.xls",
    ]
    df = None

    for file_name in possible_files:
        file_path = os.path.join(BASE_DIR, file_name)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            break

    if df is None:
        st.error(
            "❌ Dataset File Not Found! GitHub वर फाईल 'RTA Dataset.xls' किंवा 'RTA Dataset.csv' या नावाने अपलोड झाली आहे का ते तपासा."
        )
        st.stop()

    # Missing values handle karna
    df = df.fillna("Unknown")
    return df


df = load_data()

# ----------------- SIDEBAR FILTERS -----------------
st.sidebar.header("🔍 Filters")

# Filter 1: Day of Week (City ki jagah Day_of_week use kiya hai)
all_days = list(df["Day_of_week"].unique())
selected_days = st.sidebar.multiselect(
    "Select Day of Week:", options=all_days, default=all_days
)

# Filter 2: Accident Severity
all_severities = list(df["Accident_severity"].unique())
selected_severities = st.sidebar.multiselect(
    "Select Severity Level:", options=all_severities, default=all_severities
)

# Apply Filters to Data
filtered_df = df[
    (df["Day_of_week"].isin(selected_days))
    & (df["Accident_severity"].isin(selected_severities))
]

# ----------------- KEY METRICS -----------------
st.subheader("📈 Key Metrics")

total_accidents = len(filtered_df)

# Total Casualties calculation
if "Number_of_casualties" in filtered_df.columns:
    total_casualties = pd.to_numeric(
        filtered_df["Number_of_casualties"], errors="coerce"
    ).sum()
else:
    total_casualties = 0

# Fatal Accidents count
fatal_accidents = len(
    filtered_df[
        filtered_df["Accident_severity"].str.contains(
            "Fatal", case=False, na=False
        )
    ]
)

# Avg Casualties per Accident
avg_casualties = (
    round(total_casualties / total_accidents, 2) if total_accidents > 0 else 0
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Accidents", f"{total_accidents:,}")
col2.metric("Total Casualties", f"{int(total_casualties):,}")
col3.metric("Fatal Accidents", f"{fatal_accidents:,}")
col4.metric("Avg Casualties / Accident", avg_casualties)

st.markdown("---")

# ----------------- CHARTS & ANALYSIS -----------------
st.subheader("📊 Accident Analysis Charts")

chart_col1, chart_col2 = st.columns(2)

# Chart 1: Accidents by Day of Week & Severity (Replacing City)
with chart_col1:
    st.markdown("### Accidents by Day & Severity")
    day_severity_df = (
        filtered_df.groupby(["Day_of_week", "Accident_severity"])
        .size()
        .reset_index(name="Count")
    )

    fig_day = px.bar(
        day_severity_df,
        x="Day_of_week",
        y="Count",
        color="Accident_severity",
        barmode="group",
        labels={"Day_of_week": "Day of Week", "Count": "Number of Accidents"},
        template="plotly_dark",
    )
    st.plotly_chart(fig_day, use_container_width=True)

# Chart 2: Impact of Weather Conditions
with chart_col2:
    st.markdown("### Impact of Weather Conditions")
    weather_df = filtered_df["Weather_conditions"].value_counts().reset_index()
    weather_df.columns = ["Weather_conditions", "Count"]

    fig_weather = px.pie(
        weather_df,
        names="Weather_conditions",
        values="Count",
        hole=0.4,
        template="plotly_dark",
    )
    st.plotly_chart(fig_weather, use_container_width=True)

# ----------------- EXTRA ANALYSIS -----------------
st.markdown("---")
chart_col3, chart_col4 = st.columns(2)

# Chart 3: Top Causes of Accidents
with chart_col3:
    st.markdown("### Top Causes of Accidents")
    cause_df = (
        filtered_df["Cause_of_accident"].value_counts().head(7).reset_index()
    )
    cause_df.columns = ["Cause", "Count"]

    fig_cause = px.bar(
        cause_df,
        x="Count",
        y="Cause",
        orientation="h",
        color="Count",
        template="plotly_dark",
    )
    st.plotly_chart(fig_cause, use_container_width=True)

# Chart 4: Accidents by Vehicle Type
with chart_col4:
    st.markdown("### Accidents by Vehicle Type")
    vehicle_df = (
        filtered_df["Type_of_vehicle"].value_counts().head(7).reset_index()
    )
    vehicle_df.columns = ["Vehicle_Type", "Count"]

    fig_vehicle = px.bar(
        vehicle_df,
        x="Vehicle_Type",
        y="Count",
        color="Count",
        template="plotly_dark",
    )
    st.plotly_chart(fig_vehicle, use_container_width=True)


# ----------------- DOWNLOAD BUTTON -----------------
st.markdown("---")


@st.cache_data
def convert_df(data_frame):
    return data_frame.to_csv(index=False).encode("utf-8")


csv_data = convert_df(filtered_df)
st.download_button(
    label="📥 Download Clean Dataset (CSV)",
    data=csv_data,
    file_name="Cleaned_RTA_Dataset.csv",
    mime="text/csv",
)
