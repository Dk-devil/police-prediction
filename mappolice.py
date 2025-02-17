import streamlit as st
import pickle
import numpy as np
from streamlit_folium import st_folium
import folium
from folium import plugins
from shapely.geometry import Polygon
import geopandas as gpd

# Load trained model
with open('police_prediction_model.pkl', 'rb') as file:
    model = pickle.load(file)

# Streamlit App
st.set_page_config(page_title="Police Requirement Prediction", layout="centered")

st.title("Police Requirement Prediction App")
st.markdown("#### Estimate the number of policemen needed based on area, gates, population, and security risk.")

# Map for area selection
st.subheader("Select Area on Map")
st.write("Draw a polygon to calculate the area in square meters.")

m = folium.Map(location=[13.0827, 80.2707], zoom_start=15)
draw = plugins.Draw(
    export=True,
    position='topleft',
    draw_options={
        'polyline': False,
        'rectangle': False,
        'circle': False,
        'marker': False,
        'polygon': True,
    },
    edit_options={'edit': True}
)
draw.add_to(m)

map_data = st_folium(m, width=700, height=500)

area_sq_m = 0
if map_data and map_data['last_active_drawing']:
    geometry = map_data['last_active_drawing']['geometry']['coordinates'][0]
    polygon = Polygon(geometry)
    gdf = gpd.GeoDataFrame(index=[0], geometry=[polygon], crs="EPSG:4326")
    gdf = gdf.to_crs(epsg=3857)
    area_sq_m = gdf.geometry.area.iloc[0]
    st.success(f"Area Selected: {area_sq_m:.2f} square meters")

# User Input Fields
no_of_gates = st.number_input("Enter Number of Gates", min_value=0, step=1, format="%d")
population = st.number_input("Enter Population", min_value=0, step=1, format="%d")
security_risk = st.selectbox(
    "Select Security Risk Level", [1, 2, 3], format_func=lambda x: {1: 'Low', 2: 'Medium', 3: 'High'}[x]
)

# Population Density Calculation
population_density = population / area_sq_m if area_sq_m > 0 else 0

# Predict Button
if st.button("🔍 Predict Number of Policemen"):
    if area_sq_m <= 0:
        st.error("Please select a valid area on the map.")
    else:
        input_features = np.array([[area_sq_m, no_of_gates, population_density, security_risk]])
        prediction = model.predict(input_features)
        st.success(f" Estimated Number of Policemen Needed: {int(round(prediction[0]))}")

st.markdown("---")
