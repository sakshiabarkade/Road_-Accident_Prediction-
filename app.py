import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(
    page_title="Road Accident Survey Dashboard",
    page_icon="🚨",
    layout="wide"
)

# Title & Description
st.title("🚨 Road Accident Survey & Analysis Dashboard")
st.markdown("Yeh dashboard road accident survey data ko analyze aur visualize karne ke liye banaya gaya hai.")

# Dummy Data Load / Real Data Upload Functionality
@st.cache_data
def load_data():
    # Sample data setup - Aap yahan aapka real CSV file substitute kar sakte hain:
    # df = pd.read_csv('your_accident_data.csv')
    data = {
        'Accident_ID': range(101, 121),
        'City': ['Mumbai', 'Delhi', 'Bangalore', 'Mumbai', 'Pune', 'Delhi', 'Pune', 'Bangalore', 'Mumbai', 'Delhi',
                 'Pune', 'Bangalore', 'Mumbai', 'Delhi', 'Pune', 'Bangalore', 'Mumbai', 'Delhi', 'Pune', 'Bangalore'],
        'Severity': ['Minor', 'Fatal', 'Serious', 'Minor', 'Serious', 'Fatal', 'Minor', 'Serious', 'Minor', 'Fatal',
                     'Minor', 'Serious', 'Fatal', 'Minor', 'Serious', 'Minor', 'Serious', 'Fatal', 'Minor', 'Serious'],
        'Weather': ['Clear', 'Rainy', 'Foggy', 'Clear', 'Rainy', 'Foggy', 'Clear', 'Clear', 'Rainy', 'Foggy',
                    'Clear', 'Rainy', 'Foggy', 'Clear', 'Rainy', 'Foggy', 'Clear', 'Clear', 'Rainy', 'Foggy'],
        'Time_of_Day': ['Night', 'Day', 'Night', 'Day', 'Night', 'Night', 'Day', 'Day', 'Night', 'Day',
                       'Night', 'Day', 'Night', 'Day', 'Night', 'Night', 'Day', 'Day', 'Night', 'Day'],
        'Casualties': [1, 3, 2, 1, 2, 4, 1, 2, 1, 3, 1, 2, 4, 1, 2, 1, 2, 3, 1, 2]
    }
    return pd.DataFrame(data)

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filters")

selected_city = st.sidebar.multiselect(
    "Select City:",
    options=df['City'].unique(),
    default=df['City'].unique()
)

selected_severity = st.sidebar.multiselect(
    "Select Severity Level:",
    options=df['Severity'].unique(),
    default=df['Severity'].unique()
)

# Filtering Data
filtered_df = df[(df['City'].isin(selected_city)) & (df['Severity'].isin(selected_severity))]

# --- MAIN DASHBOARD KPI METRICS ---
st.markdown("### 📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Accidents", len(filtered_df))
col2.metric("Total Casualties", filtered_df['Casualties'].sum())
col3.metric("Fatal Accidents", len(filtered_df[filtered_df['Severity'] == 'Fatal']))
col4.metric("Avg Casualties / Accident", round(filtered_df['Casualties'].mean(), 2) if len(filtered_df) > 0 else 0)

st.divider()

# --- VISUALIZATIONS ---
st.markdown("### 📊 Accident Analysis Charts")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Accidents by City & Severity")
    fig_city = px.bar(
        filtered_df, 
        x='City', 
        color='Severity', 
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_city, use_container_width=True)

with chart_col2:
    st.subheader("Impact of Weather Conditions")
    fig_weather = px.pie(
        filtered_df, 
        names='Weather', 
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_weather, use_container_width=True)

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.subheader("Accidents: Day vs Night")
    fig_time = px.histogram(
        filtered_df, 
        x='Time_of_Day', 
        color='Severity',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_time, use_container_width=True)

with chart_col4:
    st.subheader("Casualties Distribution")
    fig_casualty = px.box(
        filtered_df, 
        x='Severity', 
        y='Casualties', 
        color='Severity'
    )
    st.plotly_chart(fig_casualty, use_container_width=True)

# --- DATA TABLE ---
st.divider()
st.markdown("### 📄 Raw Survey Data")
st.dataframe(filtered_df, use_container_width=True)
