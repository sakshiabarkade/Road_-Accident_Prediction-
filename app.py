import os
import glob
import pandas as pd
import streamlit as st
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Road Accident Survey & Analysis Dashboard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Theme Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
    }
    div[data-testid="stMetricValue"] {
        font-size: 38px;
        font-weight: bold;
        color: #FFFFFF;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 16px;
        color: #A0AAB4;
    }
    </style>
""", unsafe_allow_html=True)

# --- SMART LOAD DATA FUNCTION ---
@st.cache_data
def load_data():
    # File options in order of priority
    possible_files = [
        'RTA Dataset.csv',
        'RTA Dataset.xls',
        'RTA Dataset.xlsx'
    ]
    
    # Also search for any matching dynamic pattern in repository
    found_files = glob.glob('*RTA*') + glob.glob('*rta*') + glob.glob('*.csv') + glob.glob('*.xls*')
    all_targets = possible_files + found_files

    for file_path in all_targets:
        if os.path.exists(file_path):
            try:
                # First try reading as CSV
                return pd.read_csv(file_path)
            except Exception:
                try:
                    # Fallback to Excel reader
                    return pd.read_excel(file_path)
                except Exception:
                    continue
                    
    # If no file found at all
    st.error("❌ Dataset file nahi mili! Kripya check karein ki 'RTA Dataset.csv' ya 'RTA Dataset.xls' GitHub repo me uploaded hai ya nahi.")
    st.stop()

df = load_data()

# --- TITLE & HEADER ---
st.title("🚨 Road Accident Survey & Analysis Dashboard")
st.markdown("Yeh dashboard road accident survey data ko analyze aur visualize karne ke liye banaya gaya hai.")

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filters")

# Filter 1: Area Type (Replacing City)
if 'Area_accident_occured' in df.columns:
    all_areas = df['Area_accident_occured'].dropna().unique().tolist()
    selected_area = st.sidebar.multiselect(
        "Select Area Type:",
        options=all_areas,
        default=all_areas[:5] if len(all_areas) >= 5 else all_areas
    )
else:
    all_areas = []
    selected_area = []

# Filter 2: Severity Level
if 'Accident_severity' in df.columns:
    all_severities = df['Accident_severity'].dropna().unique().tolist()
    selected_severity = st.sidebar.multiselect(
        "Select Severity Level:",
        options=all_severities,
        default=all_severities
    )
else:
    all_severities = []
    selected_severity = []

# Filtering Data Based on Selections
filtered_df = df.copy()
if selected_area and 'Area_accident_occured' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Area_accident_occured'].isin(selected_area)]
if selected_severity and 'Accident_severity' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Accident_severity'].isin(selected_severity)]

# --- KEY METRICS (KPIs) ---
st.markdown("### 📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

total_accidents = len(filtered_df)
total_casualties = filtered_df['Number_of_casualties'].sum() if ('Number_of_casualties' in filtered_df.columns and total_accidents > 0) else 0

if 'Accident_severity' in filtered_df.columns:
    fatal_accidents = len(filtered_df[filtered_df['Accident_severity'].astype(str).str.contains('Fatal', case=False, na=False)])
else:
    fatal_accidents = 0

avg_casualties = round(filtered_df['Number_of_casualties'].mean(), 2) if ('Number_of_casualties' in filtered_df.columns and total_accidents > 0) else 0

col1.metric("Total Accidents", f"{total_accidents:,}")
col2.metric("Total Casualties", f"{total_casualties:,}")
col3.metric("Fatal Accidents", f"{fatal_accidents:,}")
col4.metric("Avg Casualties / Accident", avg_casualties)

st.divider()

# --- ACCIDENT ANALYSIS CHARTS ---
st.markdown("### 📊 Accident Analysis Charts")

chart_col1, chart_col2 = st.columns(2)

# Chart 1: Accidents by Area & Severity (Bar Chart)
with chart_col1:
    st.subheader("Accidents by Area & Severity")
    if not filtered_df.empty and 'Area_accident_occured' in filtered_df.columns and 'Accident_severity' in filtered_df.columns:
        fig_area = px.bar(
            filtered_df, 
            x='Area_accident_occured', 
            color='Accident_severity', 
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Set2,
            template="plotly_dark"
        )
        fig_area.update_layout(
            xaxis_title="Area Type",
            yaxis_title="Count",
            legend_title="Severity",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_area, use_container_width=True)
    else:
        st.info("No data available for selected filters.")

# Chart 2: Impact of Weather Conditions (Donut Chart)
with chart_col2:
    st.subheader("Impact of Weather Conditions")
    if not filtered_df.empty and 'Weather_conditions' in filtered_df.columns:
        fig_weather = px.pie(
            filtered_df, 
            names='Weather_conditions', 
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.RdBu,
            template="plotly_dark"
        )
        fig_weather.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_weather, use_container_width=True)
    else:
        st.info("No data available for selected filters.")

chart_col3, chart_col4 = st.columns(2)

# Chart 3: Accidents by Day of Week (Histogram)
with chart_col3:
    st.subheader("Accidents by Day of Week")
    if not filtered_df.empty and 'Day_of_week' in filtered_df.columns and 'Accident_severity' in filtered_df.columns:
        fig_day = px.histogram(
            filtered_df, 
            x='Day_of_week', 
            color='Accident_severity',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            template="plotly_dark"
        )
        fig_day.update_layout(
            xaxis_title="Day of Week",
            yaxis_title="Count",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_day, use_container_width=True)
    else:
        st.info("No data available for selected filters.")

# Chart 4: Top Causes of Accidents (Horizontal Bar Chart)
with chart_col4:
    st.subheader("Top Causes of Accidents")
    if not filtered_df.empty and 'Cause_of_accident' in filtered_df.columns:
        cause_counts = filtered_df['Cause_of_accident'].value_counts().reset_index()
        cause_counts.columns = ['Cause', 'Count']
        fig_cause = px.bar(
            cause_counts.head(6), 
            x='Count', 
            y='Cause', 
            orientation='h',
            color='Count',
            color_continuous_scale='Reds',
            template="plotly_dark"
        )
        fig_cause.update_layout(
            yaxis=dict(autorange="reverse"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_cause, use_container_width=True)
    else:
        st.info("No data available for selected filters.")

# --- RAW DATA VIEW ---
st.divider()
st.markdown("### 📄 Filtered Data Preview")
st.dataframe(filtered_df, use_container_width=True)
