import streamlit as st
import pickle
import numpy as np

# Load trained model
with open('police_prediction_model.pkl', 'rb') as file:
    model = pickle.load(file)

# Streamlit App
st.set_page_config(page_title="Police Requirement Prediction", page_icon="🚓", layout="centered")

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main { background-color: #f4f4f9; }
    .stButton>button { background-color: #4CAF50; color: white; font-size: 16px; padding: 10px 24px; border-radius: 8px; }
    .stNumberInput>div>div>input { font-size: 16px; }
    .stSelectbox>div>div>select { font-size: 16px; }
    .stTitle { color: #2e3b4e; }
    </style>
    """, unsafe_allow_html=True)

# Title Section
st.title("Police Requirement Prediction App")
st.markdown("#### Estimate the number of policemen needed based on area, gates, population, and security risk.")

# User Input Fields
area_sq_m = st.number_input(" Enter Area (square meters)", min_value=0, step=1, format="%d")
no_of_gates = st.number_input("Enter Number of Gates", min_value=0, step=1, format="%d")
population = st.number_input(" Enter Population", min_value=0, step=1, format="%d")
security_risk = st.selectbox(
    " Select Security Risk Level",
    [1, 2, 3],
    format_func=lambda x: {1: 'Low', 2: 'Medium', 3: 'High'}[x]
)

# Population Density Calculation
population_density = population / area_sq_m if area_sq_m > 0 else 0

# Predict Button
if st.button("🔍 Predict Number of Policemen"):
    input_features = np.array([[area_sq_m, no_of_gates, population_density, security_risk]])
    prediction = model.predict(input_features)
    st.success(f"🚔 Estimated Number of Policemen Needed: {int(round(prediction[0]))}")

# Footer
st.markdown("---")

