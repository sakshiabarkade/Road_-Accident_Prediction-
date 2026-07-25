import joblib
import pandas as pd
import streamlit as st

# ------------------------------------------------------------------------------
# 1. PAGE SETUP & MODERN STYLING (Aesthetic UI)
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Road Safety Predictor", page_icon="⚡", layout="wide"
)

# Custom CSS for Aesthetics & Smooth UX
st.markdown(
    """
    <style>
    .main { padding-top: 1.5rem; }
    
    /* Modern Button Styling */
    .stButton>button {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
    }
    
    /* Container Styling */
    [data-testid="stForm"] {
        border-radius: 15px;
        padding: 25px;
        background-color: #ffffff;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid #eef2f5;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------------------
# 2. FAST MODEL LOADING (Caching to prevent lag)
# ------------------------------------------------------------------------------
@st.cache_resource
def load_assets():
    try:
        model = joblib.load("xgb_accident_model.pkl")
        encoders = joblib.load("label_encoders.pkl")
        target_encoder = joblib.load("target_encoder.pkl")
        return model, encoders, target_encoder
    except Exception as e:
        return None, None, None


model, encoders, target_encoder = load_assets()

# ------------------------------------------------------------------------------
# 3. HEADER
# ------------------------------------------------------------------------------
st.title("🚨 Accident Severity Risk Predictor")
st.caption(
    "⚡ Instant accident severity insights using your AI Accident Assessment Model."
)

if model is None:
    st.error(
        "⚠️ Model files not found! Please ensure 'xgb_accident_model.pkl', 'label_encoders.pkl', and 'target_encoder.pkl' exist in the directory."
    )
    st.stop()

# ------------------------------------------------------------------------------
# 4. INPUT FORM & LAYOUT (No Day Dropdown)
# ------------------------------------------------------------------------------
col_input, col_result = st.columns([1.2, 1], gap="large")

with col_input:
    with st.form("accident_form"):
        st.subheader("🎯 Crash Parameters")

        # Key High-Impact Parameters
        c1, c2 = st.columns(2)
        with c1:
            weather = st.selectbox(
                "🌧️ Weather", ["Clear", "Rainy", "Foggy", "Snowy"]
            )
            time = st.selectbox("🕒 Time of Day", ["Day", "Night"])
            driver_age = st.selectbox(
                "👤 Driver Age", ["18-30", "Under 18", "31-50", "Over 51"]
            )
            vehicle_relation = st.selectbox(
                "🔑 Driver Relation", ["Owner", "Employee"]
            )
            road_surface = st.selectbox(
                "🛣️ Road Surface",
                ["Asphalt roads", "Gravel roads", "Earth roads", "Other"],
            )
            type_collision = st.selectbox(
                "💥 Collision Type",
                [
                    "Vehicle with vehicle",
                    "Rollover",
                    "Collision with pedestrian",
                    "Collision with animal",
                ],
            )

        with c2:
            cause = st.selectbox(
                "⚠️ Main Cause",
                [
                    "Overspeed",
                    "No distancing",
                    "Careless driving",
                    "Overturning",
                    "Improper parking",
                ],
            )
            driver_exp = st.selectbox(
                "🪪 Driver Exp.",
                [
                    "2-5yr",
                    "Below 1yr",
                    "1-2yr",
                    "5-10yr",
                    "Above 10yr",
                    "No Licence",
                ],
            )
            service_year = st.selectbox(
                "🚘 Vehicle Age",
                ["2-5yrs", "Below 1yr", "1-2yr", "5-10yrs", "Above 10yr"],
            )
            work_casualty = st.selectbox(
                "💼 Casualty Role",
                ["Driver", "Employee", "Self-employed", "Student", "Unemployed"],
            )
            light = st.selectbox(
                "💡 Light Condition",
                [
                    "Daylight",
                    "Darkness - lights lit",
                    "Darkness - no lighting",
                ],
            )
            vehicle_movement = st.selectbox(
                "🔄 Movement",
                [
                    "Going straight",
                    "U-turn",
                    "Reversing",
                    "Overtaking",
                    "Waiting to go",
                ],
            )

        st.markdown("---")
        vehicles_involved = st.slider("🚗 Vehicles Involved", 1, 10, 2)
        casualties = st.slider("🩹 Number of Casualties", 1, 10, 1)

        submit = st.form_submit_button("⚡ Analyze Severity", use_container_width=True)

# ------------------------------------------------------------------------------
# 5. FAST PREDICTION & OUTPUT LOGIC
# ------------------------------------------------------------------------------
with col_result:
    st.subheader("📊 Instant Risk Assessment")

    if submit:
        try:
            # Model ke liye DataFrame बनाना (Day = Monday Default silent pass)
            input_dict = {
                "Time": [time],
                "Day_of_week": ["Monday"],  # Silent Default Pass
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
                "Number_of_casualties": [int(casualties)],
            }

            input_df = pd.DataFrame(input_dict)

            # Fast Encoding Processing
            for col in input_df.columns:
                if col in encoders:
                    le = encoders[col]
                    val = str(input_df[col].iloc[0]).strip().lower()
                    class_map = {str(c).strip().lower(): c for c in le.classes_}

                    if val in class_map:
                        input_df[col] = le.transform([class_map[val]])[0]
                    else:
                        input_df[col] = le.transform([le.classes_[0]])[0]

            # Fast Inference
            pred = model.predict(input_df)[0]
            pred_label = str(target_encoder.inverse_transform([pred])[0])
            pred_lower = pred_label.lower()

            # Beautiful Aesthetic Cards
            if "slight" in pred_lower:
                st.success(f"### 🟢 Prediction: {pred_label.upper()}")
                st.info(
                    "Low risk crash environment detected. Minor damage predicted."
                )

            elif "serious" in pred_lower:
                st.warning(f"### 🟡 Prediction: {pred_label.upper()}")
                st.write(
                    "Moderate to High impact risk detected. Safety interventions required."
                )

            elif "fatal" in pred_lower:
                st.error(f"### 🔴 Prediction: {pred_label.upper()}")
                st.error(
                    "🚨 High probability of fatal outcome! Critical severity level detected."
                )

            else:
                st.error(f"### 🔴 Prediction: {pred_label.upper()}")
                st.write(
                    "Critical severity level predicted. Immediate safety measures recommended."
                )

        except Exception as e:
            st.error(f"Prediction Error: {e}")
    else:
        st.info(
            "👈 Select parameters on the left and click **Analyze Severity** to evaluate crash severity."
        )
