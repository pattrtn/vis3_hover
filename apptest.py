import json
import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np

# Load the GeoJSON file for provinces
geojson_file_path_1 = "gadm41_THA_1.json"
with open(geojson_file_path_1, "r", encoding="utf-8") as f:
    geojson_data_1 = json.load(f)

# Load the CSV file for province percentages
csv_file_path = "./Percentage_of_Correct_Predictions_by_Province.csv"
data = pd.read_csv(csv_file_path)

# Create a dictionary for quick lookup of percentage by province
province_percentage = data.set_index('province_input')['percentage_true'].to_dict()

# Create a Streamlit app
st.title("Thailand Provinces Map with Percentage Heatmap")

# Initialize the map centered at Thailand
map_1 = folium.Map(location=[13.736717, 100.523186], zoom_start=6)

# Function to get tooltip text for provinces
def get_tooltip_text_province(name):
    clean_name = name.replace("จังหวัด", "")
    percentage = province_percentage.get(clean_name, "N/A")
    return f"{clean_name}: {percentage}%"

# Updated color function to use red scale
def get_color_province(percentage):
    # Handle "N/A" case
    if percentage == "N/A":
        return "grey"
    
    # Convert percentage to float
    percentage = float(percentage)
    
    # Assign color based on percentage
    if percentage > 75:
        return "#8B0000"  # Dark red (high percentage)
    elif percentage > 50:
        return "#B22222"  # Firebrick red
    elif percentage > 25:
        return "#DC143C"  # Crimson red
    else:
        return "#FF6347"  # Tomato red (low percentage)

# Add GeoJSON polygons for provinces
for feature in geojson_data_1["features"]:
    name = feature["properties"]["NL_NAME_1"]  # Extract province name
    tooltip_text = get_tooltip_text_province(name)
    clean_name = name.replace("จังหวัด", "")
    percentage = province_percentage.get(clean_name, "N/A")
    color = get_color_province(percentage)  # Get color for this province
    
    # Add GeoJSON features to map with dynamic color
    folium.GeoJson(
        feature,
        tooltip=tooltip_text,
        style_function=lambda feature, color=color: {
            "fillColor": color,  # Set the dynamic color
            "color": "black",     # Set border color
            "weight": 1,          # Set border width
            "fillOpacity": 0.5    # Set transparency of the fill
        }
    ).add_to(map_1)

# Display the map in Streamlit
st.subheader("Provinces Heatmap")
st_folium(map_1, width=800, height=600)
