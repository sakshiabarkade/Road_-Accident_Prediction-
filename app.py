import streamlit as st
import pandas as pd
import joblib

# -----------------------------
# 1. Load Model and Encoders
# -----------------------------
@st.cache_resource
def load_assets():
    try:
        model = joblib.load("xgb_accident_model.pkl")
        encoders = joblib.load("label_encoders.pkl")
        target_encoder = joblib.load("target_encoder.pkl")
        return model, encoders, target_encoder
    except Exception as e:
        st.error(f"Error loading model files: {e}")
        return None, None, None

model, encoders, target_encoder = load_assets()

# -----------------------------
# 2. Streamlit Page Setup
# -----------------------------
st.set_page_config(
    page_title="Road Accident Severity Prediction",
    page_icon="🚧",
    layout="centered"
)

st.title("🚧 Road Accident Severity Prediction")
st.markdown("Enter the accident details below to predict severity.")

# -----------------------------
# 3. Input Options
# -----------------------------
options_time = ["Day", "Night"]
options_day = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
options_age = ['Under 18', '18-30', '31-50', 'Over 51']
options_driver_exp = ['Below 1yr', '1-2yr', '2-5yr', '5-10yr', 'Above 10yr', 'No Licence']
options_vehicle_relation = ['Employee', 'Owner']
options_service_year = ['Below 1yr', '1-2yr', '2-5yrs', '5-10yrs', 'Above 10yr']
options_road_surface_type = ['Asphalt roads', 'Gravel roads', 'Earth roads', 'Other']
options_weather = ['Clear', 'Rainy', 'Foggy', 'Snowy']
options_light = ['Daylight', 'Darkness - lights lit', 'Darkness - no lighting']
options_type_of_collision = ['Vehicle with vehicle', 'Rollover', 'Collision with pedestrian', 'Collision with animal']
options_vehicle_movement = ['Going straight', 'U-turn', 'Reversing', 'Overtaking', 'Waiting to go']
options_work_of_casualty = ['Driver', 'Employee', 'Self-employed', 'Student', 'Unemployed']
options_cause = ['Overspeed', 'No distancing', 'Careless driving', 'Overturning', 'Improper parking']

# -----------------------------
# 4. Input Form
# -----------------------------
with st.form("prediction_form"):
    st.subheader("📝 Enter details below:")

    time = st.selectbox("Select Time of Day", options_time)
    day = st.selectbox("Day of Week", options_day)
    driver_age = st.selectbox("Driver Age Band", options_age)
    driver_exp = st.selectbox("Driving Experience", options_driver_exp)
    vehicle_relation = st.selectbox("Vehicle Driver Relation", options_vehicle_relation)
    service_year = st.selectbox("Vehicle Service Year", options_service_year)
    road_surface = st.selectbox("Road Surface Type", options_road_surface_type)
    weather = st.selectbox("Weather Condition", options_weather)
    light = st.selectbox("Light Condition", options_light)
    type_collision = st.selectbox("Type of Collision", options_type_of_collision)
    vehicle_movement = st.selectbox("Vehicle Movement", options_vehicle_movement)
    work_casualty = st.selectbox("Work of Casualty", options_work_of_casualty)
    cause = st.selectbox("Cause of Accident", options_cause)
    vehicles_involved = st.slider("Number of Vehicles Involved", 1, 10, 1)
    casualties = st.slider("Number of Casualties", 1, 10, 1)

    submit = st.form_submit_button("🚦 Predict Severity")

# -----------------------------
# 5. Prediction Logic
# -----------------------------
if submit:
    if model is None:
        st.error("Model not loaded properly.")
    else:
        try:
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
                "Number_of_vehicles_involved": [vehicles_involved],
                "Number_of_casualties": [casualties]
            }

            input_df = pd.DataFrame(input_dict)

            # Text cleaning
            for col in input_df.select_dtypes(include="object").columns:
                input_df[col] = input_df[col].astype(str).str.strip().str.lower()

            # Encode categorical features
            for col, le in encoders.items():
                if col in input_df.columns:
                    known_classes = [str(c).lower() for c in le.classes_]
                    input_df[col] = input_df[col].apply(
                        lambda x: le.transform([x])[0] if x in known_classes else -1
                    )

            # Predict
            pred = model.predict(input_df)[0]
            pred_label = str(target_encoder.inverse_transform([pred])[0])

            # Output UI
            st.subheader("Prediction Result:")
            if "slight" in pred_label.lower():
                st.success(f"Severity: {pred_label}")
            elif "serious" in pred_label.lower():
                st.warning(f"Severity: {pred_label}")
            else:
                st.error(f"Severity: {pred_label}")

        except Exception as e:
            st.error(f"Prediction Error: {e}")
