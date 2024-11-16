import json
import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd

# Load the GeoJSON file
geojson_file_path = "gadm41_THA_1.json"
with open(geojson_file_path, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Load the CSV file for province percentages
csv_file_path = "/mnt/data/Percentage_of_Correct_Predictions_by_Province.csv"
data = pd.read_csv(csv_file_path)

# Create a dictionary for quick lookup of percentage by province
province_percentage = data.set_index('province_input')['percentage_true'].to_dict()

# Create a Streamlit app
st.title("Thailand Provinces - Hover for Names and Data")

# Initialize the map centered at Thailand
m = folium.Map(location=[13.736717, 100.523186], zoom_start=6)

# Add GeoJSON polygons with tooltips and percentage data
def get_tooltip_text(name):
    # Remove "จังหวัด" from NL_NAME_1 if present
    clean_name = name.replace("จังหวัด", "")
    percentage = province_percentage.get(clean_name, "N/A")  # Default to "N/A" if not found
    return f"{clean_name}: {percentage}%"

for feature in geojson_data["features"]:
    name = feature["properties"]["NL_NAME_1"]  # Extract province name
    tooltip_text = get_tooltip_text(name)
    folium.GeoJson(
        feature,
        tooltip=tooltip_text,  # Set the tooltip to display NAME_1 and percentage
        style_function=lambda x: {
            "fillColor": "blue",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5,
        },
    ).add_to(m)

# Display the map in Streamlit
st_folium(m, width=800, height=600)
