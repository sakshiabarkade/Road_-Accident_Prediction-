import streamlit as st
import pandas as pd
import joblib

# ------------------------------------------------------------------------------
# 1. PAGE SETUP & MODERN STYLING
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Road Safety Predictor",
    page_icon="⚡",
    layout="wide"
)

# Modern UI Styling (Soft shadows, rounded corners, clean fonts)
st.markdown("""
    <style>
    .main { padding-top: 1.5rem; }
    
    .stButton>button {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    .card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #eef2f5;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. MODEL & ENCODER LOADING
# ------------------------------------------------------------------------------
@st.cache_resource
def load_assets():
    try:
        model = joblib.load("xgb_accident_model.pkl")
        encoders = joblib.load("label_encoders.pkl")
        target_encoder = joblib.load("target_encoder.pkl")
        return model, encoders, target_encoder
    except Exception as e:
        st.error(f"⚠️ Error loading model files: {e}")
        return None, None, None

model, encoders, target_encoder = load_assets()

# ------------------------------------------------------------------------------
# 3. HEADER
# ------------------------------------------------------------------------------
st.title("🚨 Quick Accident Risk Estimator")
st.caption("⚡ Get instant accident severity insights in less than 5 seconds using 4 key metrics.")

# ------------------------------------------------------------------------------
# 4. FAST 4-INPUT UI LAYOUT
# ------------------------------------------------------------------------------
col_input, col_result = st.columns([1.1, 1], gap="large")

with col_input:
    st.subheader("🎯 Key Impact Factors")
    
    # 4 High-Impact Inputs
    weather = st.selectbox("🌧️ Weather Condition", ['Clear', 'Rainy', 'Foggy', 'Snowy'])
    cause = st.selectbox("⚠️ Primary Cause", ['Overspeed', 'No distancing', 'Careless driving', 'Overturning', 'Improper parking'])
    vehicles_involved = st.slider("🚗 Vehicles Involved", 1, 10, 2)
    casualties = st.slider("🩹 Number of Casualties", 1, 10, 1)

    # Advanced Settings (Hidden by default so users aren't overwhelmed)
    with st.expander("⚙️ Advanced Parameters (Optional)", expanded=False):
        time = st.selectbox("Time of Day", ["Day", "Night"])
        day = st.selectbox("Day of Week", ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])
        driver_age = st.selectbox("Driver Age Band", ['18-30', 'Under 18', '31-50', 'Over 51'])
        driver_exp = st.selectbox("Driving Experience", ['2-5yr', 'Below 1yr', '1-2yr', '5-10yr', 'Above 10yr', 'No Licence'])
        road_surface = st.selectbox("Road Surface", ['Asphalt roads', 'Gravel roads', 'Earth roads', 'Other'])
        light = st.selectbox("Light Condition", ['Daylight', 'Darkness - lights lit', 'Darkness - no lighting'])
        type_collision = st.selectbox("Type of Collision", ['Vehicle with vehicle', 'Rollover', 'Collision with pedestrian', 'Collision with animal'])
        vehicle_movement = st.selectbox("Vehicle Movement", ['Going straight', 'U-turn', 'Reversing', 'Overtaking', 'Waiting to go'])
        vehicle_relation = 'Owner'
        service_year = '2-5yrs'
        work_casualty = 'Driver'

    submit = st.button("⚡ Analyze Severity", use_container_width=True)

# -----------------------------
# 5. PREDICTION & OUTPUT LOGIC
# -----------------------------
if "slight" in pred_lower:
    st.success(f"### 🟢 Prediction: {pred_label.upper()}")
    st.info("Low risk crash environment detected. Minor damage predicted.")

elif "serious" in pred_lower:
    st.warning(f"### 🟡 Prediction: {pred_label.upper()}")
    st.write(
        "Moderate to High impact risk detected. Safety interventions required."
    )

elif "fatal" in pred_lower:
    st.error(f"### 🔴 Prediction: {pred_label.upper()}")
    st.error(
        "🚨 High probability of fatal outcome! Extreme safety protocol required."
    )

else:
    st.error(f"### 🔴 Prediction: {pred_label.upper()}")
    st.write(
        "Critical severity level predicted. Immediate safety measures recommended."
    )
