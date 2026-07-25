import streamlit as st
import pandas as pd
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

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        # File is originally in CSV format despite .xls extension
        df = pd.read_csv('RTA Dataset.xls')
    except Exception:
        try:
            df = pd.read_excel('RTA Dataset.xls')
        except Exception:
            df = pd.read_csv('RTA Dataset.csv')
    return df

df = load_data()

# --- TITLE & HEADER ---
st.title("🚨 Road Accident Survey & Analysis Dashboard")
st.markdown("Yeh dashboard road accident survey data ko analyze aur visualize karne ke liye banaya gaya hai.")

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filters")

# Filter 1: Area Type (Replacing City)
all_areas = df['Area_accident_occured'].dropna().unique().tolist()
selected_area = st.sidebar.multiselect(
    "Select Area Type:",
    options=all_areas,
    default=all_areas[:5] if len(all_areas) >= 5 else all_areas
)

# Filter 2: Severity Level
all_severities = df['Accident_severity'].dropna().unique().tolist()
selected_severity = st.sidebar.multiselect(
    "Select Severity Level:",
    options=all_severities,
    default=all_severities
)

# Filter Data Based on User Selection
filtered_df = df[
    (df['Area_accident_occured'].isin(selected_area)) & 
    (df['Accident_severity'].isin(selected_severity))
]

# --- KEY METRICS (KPIs) ---
st.markdown("### 📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

total_accidents = len(filtered_df)
total_casualties = filtered_df['Number_of_casualties'].sum() if total_accidents > 0 else 0
fatal_accidents = len(filtered_df[filtered_df['Accident_severity'].str.contains('Fatal', case=False, na=False)])
avg_casualties = round(filtered_df['Number_of_casualties'].mean(), 2) if total_accidents > 0 else 0

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
    if not filtered_df.empty:
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
    if not filtered_df.empty:
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
    if not filtered_df.empty:
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
    if not filtered_df.empty:
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
