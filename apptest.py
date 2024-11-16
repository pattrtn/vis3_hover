import json
import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors  # Correctly import the colors module

# Load the GeoJSON file for provinces
geojson_file_path_1 = "gadm41_THA_1.json"
with open(geojson_file_path_1, "r", encoding="utf-8") as f:
    geojson_data_1 = json.load(f)

# Load the GeoJSON file for districts
geojson_file_path_2 = "gadm41_THA_2.json"
with open(geojson_file_path_2, "r", encoding="utf-8") as f:
    geojson_data_2 = json.load(f)

# Load the CSV file for province percentages
csv_file_path = "./Percentage_of_Correct_Predictions_by_Province.csv"
data = pd.read_csv(csv_file_path)

# Create a dictionary for quick lookup of percentage by province
province_percentage = data.set_index('province_input')['percentage_true'].to_dict()

# Create a Streamlit app
st.title("Thailand Provinces and Districts Map")

# Initialize the map centered at Thailand
map_1 = folium.Map(location=[13.736717, 100.523186], zoom_start=6)

# Function to get tooltip text for provinces
def get_tooltip_text_province(name):
    clean_name = name.replace("จังหวัด", "")
    percentage = province_percentage.get(clean_name, "N/A")
    return f"{clean_name}: {percentage}%"

# Function to get color for provinces based on the percentage (Red tone)
def get_color_province(percentage):
    if percentage == "N/A":
        return "grey"
    
    # Convert percentage to float and normalize
    percentage = float(percentage)
    normalized_percentage = np.clip(percentage / 100, 0, 1)

    # Use matplotlib's 'Reds' colormap (from white to red)
    cmap = plt.get_cmap("seismic")
    rgba_color = cmap(normalized_percentage)
    
    # Convert the RGBA color to hex
    hex_color = mcolors.rgb2hex(rgba_color[:3])
    return hex_color

# Add GeoJSON polygons for provinces
for feature in geojson_data_1["features"]:
    name = feature["properties"]["NL_NAME_1"]  # Extract province name
    tooltip_text = get_tooltip_text_province(name)
    clean_name = name.replace("จังหวัด", "")
    percentage = province_percentage.get(clean_name, "N/A")
    color = get_color_province(percentage)  # Get color for this province
    
    # Explicitly pass color here by defining a function that uses `color` for each feature
    folium.GeoJson(
        feature,
        tooltip=tooltip_text,
        style_function=lambda feature, color=color: {
            "fillColor": color,  # Set fill color dynamically
            "color": "black",  # Border color
            "weight": 1,  # Border width
            "fillOpacity": 0.5,  # Transparency of the fill
        }
    ).add_to(map_1)

# Display the first map (Provinces Heatmap)
st.subheader("Provinces Heatmap")
st_folium(map_1, width=800, height=600)

# Initialize the second map for districts
map_2 = folium.Map(location=[13.736717, 100.523186], zoom_start=6)

# Function to get tooltip text for districts
def get_tooltip_text_district(name):
    clean_name = name.replace("อำเภอ", "")  # Remove "อำเภอ" from district name
    return clean_name

# Add GeoJSON polygons for districts
for feature in geojson_data_2["features"]:
    name = feature["properties"]["NL_NAME_2"]  # Extract district name
    tooltip_text = get_tooltip_text_district(name)
    
    folium.GeoJson(
        feature,
        tooltip=tooltip_text,
        style_function=lambda x: {
            "fillColor": "blue",  # Static color for districts
            "color": "black",  # Border color
            "weight": 1,  # Border width
            "fillOpacity": 0.5,  # Transparency of the fill
        }
    ).add_to(map_2)

# Display the second map (Districts)
st.subheader("Districts Map")
st_folium(map_2, width=800, height=600)
