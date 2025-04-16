import streamlit as st
import pandas as pd
import numpy as np
import pickle
import json
import geopandas as gpd
import folium
from shapely.geometry import Polygon
from streamlit_folium import st_folium
from folium import plugins

# Load trained model & encoder (SINGLE PICKLE FILE)
with open("police_model.pkl", "rb") as model_file:
   rf_model, encoder = pickle.load(model_file)

# Streamlit UI
st.title(" Police Deployment Predictor")
st.write("Select an area on the map and enter event details to estimate police personnel requirements.")

# Interactive Folium Map
m = folium.Map(location=[13.0827, 80.2707], zoom_start=15)
draw = plugins.Draw(
    export=True,
    position='topleft',
    draw_options={'polyline': False, 'rectangle': False, 'circle': False, 'marker': False, 'polygon': True},
    edit_options={'edit': True}
)
draw.add_to(m)
map_data = st_folium(m, width=700, height=500)

# Calculate selected area
area_sq_m = 0
if map_data and map_data['last_active_drawing']:
    geometry = map_data['last_active_drawing']['geometry']['coordinates'][0]
    polygon = Polygon(geometry)
    gdf = gpd.GeoDataFrame(index=[0], geometry=[polygon], crs="EPSG:4326")
    gdf = gdf.to_crs(epsg=3857)
    area_sq_m = gdf.geometry.area.iloc[0]
    st.success(f" Area Selected: **{area_sq_m:.2f} square meters**")

# Dropdown options
vip_options = ["None", "VIP", "VVIP"]
complexity_options = ["Low", "Medium", "High"]
risk_options = ["Low", "Medium", "High"]

# User inputs
attendees = st.number_input(" Number of Attendees", min_value=1, value=100)
vip_level = st.selectbox("VIP Level", vip_options)
venue_complexity = st.selectbox(" Venue Complexity", complexity_options)
risk_level = st.selectbox("Risk Level", risk_options)

# Predict function
def predict_police_requirements(area, attendees, vip_level, venue_complexity, risk_level):
    # Encode categorical inputs
    categorical_input = pd.DataFrame([[vip_level, venue_complexity, risk_level]], 
                                     columns=["vip_factor", "venue_factor", "risk_factor"])
    
    encoded_input = [
        area,
        attendees,
        encoder['vip_factor'].transform([vip_level])[0],
        encoder['venue_factor'].transform([venue_complexity])[0],
        encoder['risk_factor'].transform([risk_level])[0]
    ]
    
    input_data = np.array([encoded_input])
    predicted_counts = rf_model.predict(input_data)[0]

    return {
        "Deputy Commissioners (DC)": int(predicted_counts[0]),
        "Assistant Commissioners (AC)": int(predicted_counts[1]),
        "Inspectors": int(predicted_counts[2]),
        "Sub-Inspectors (SIs)": int(predicted_counts[3]),
        "Officers (ORS)": int(predicted_counts[4]),
        "Armed Reserves (AR)": int(predicted_counts[5]),
        "Total Personnel": round(predicted_counts.sum())
    }

# Predict button
if st.button(" Predict Personnel Requirement"):
    if area_sq_m == 0:
        st.error(" Please select an area on the map first.")
    else:
        result = predict_police_requirements(area_sq_m, attendees, vip_level, venue_complexity, risk_level)
        
        # Display results in a table
        st.subheader(" Prediction Results")
        # st.write(f"For an event with **{attendees} attendees**, VIP Level **{vip_level}**, Venue Complexity **{venue_complexity}**, and Risk Level **{risk_level}**, the estimated police personnel required is:")

        df_result = pd.DataFrame(list(result.items()), columns=["Role", "Count"])
        st.table(df_result)

        # Highlight total personnel
        st.metric(label=" Total Personnel Required", value=result["Total Personnel"])
