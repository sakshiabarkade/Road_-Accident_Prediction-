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
# 5. PREDICTION & DEBUG LOGIC
# -----------------------------
with col_result:
    st.subheader("📊 Instant Risk Assessment")
    
    if submit:
        if model is None:
            st.error("Model artifacts not loaded.")
        else:
            try:
                # Complete Input Dictionary
                input_dict = {
                    "Time": [time],
                    "Day_of_week": [day],
                    "Age_band_of_driver": [driver_age],
                    "Driving_experience": [driver_exp],
                    "Vehicle_driver_relation": [vehicle_relation],
                    "Service_year_of_vehicle": [service_year],
                    "Road_surface_type": [road_surface],
                    "Weather_conditions": [weather],
                    "Light_conditions": [light],
                    "Type_of_collision": [type_collision],
                    "Vehicle_movement": [vehicle_movement],
                    "Work_of_casuality": [work_casualty],
                    "Cause_of_accident": [cause],
                    "Number_of_vehicles_involved": [int(vehicles_involved)],
                    "Number_of_casualties": [int(casualties)]
                }

                input_df = pd.DataFrame(input_dict)

                # Robust Categorical Encoding
                for col in input_df.columns:
                    if col in encoders:
                        le = encoders[col]
                        val = str(input_df[col].iloc[0]).strip().lower()
                        class_map = {str(c).strip().lower(): c for c in le.classes_}
                        
                        if val in class_map:
                            matched_class = class_map[val]
                            input_df[col] = le.transform([matched_class])[0]
                        else:
                            # Fallback using transform on first class
                            input_df[col] = le.transform([le.classes_[0]])[0]

                # 🔍 UNCOMMENT THIS TO DEBUG ENCODED VALUES IN STREAMLIT
                # st.write("Model Input Data:", input_df)

                # Predict
                pred = model.predict(input_df)[0]
                pred_label = str(target_encoder.inverse_transform([pred])[0])
                pred_lower = pred_label.lower()

                # Visual Output Cards
                if "slight" in pred_lower:
                    st.success(f"### 🟢 Prediction: {pred_label.upper()}")
                    st.info("Low risk crash environment detected. Minor damage predicted.")
                elif "serious" in pred_lower:
                    st.warning(f"### 🟡 Prediction: {pred_label.upper()}")
                    st.write("Moderate to High impact risk detected. Safety interventions required.")
                else:
                    st.error(f"### 🔴 Prediction: {pred_label.upper()}")
                    st.write("Critical severity level predicted. Immediate safety measures recommended.")

            except Exception as e:
                st.error(f"Prediction Error: {e}")
