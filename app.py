import json
import folium
import streamlit as st
from streamlit_folium import st_folium

# Load the GeoJSON file
geojson_file_path = "gadm41_THA_1.json"
with open(geojson_file_path, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Create a Streamlit app
st.title("Thailand Provinces - Hover for Names")

# Initialize the map centered at Thailand
m = folium.Map(location=[13.736717, 100.523186], zoom_start=6)

# Add GeoJSON polygons with tooltips
for feature in geojson_data["features"]:
    name = feature["properties"]["NAME_1"]  # Extract province name
    folium.GeoJson(
        feature,
        tooltip=name,  # Set the tooltip to display NAME_1
        style_function=lambda x: {
            "fillColor": "blue",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5,
        },
    ).add_to(m)

# Display the map in Streamlit
st_folium(m, width=800, height=600)
