import json
import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd

# Load the GeoJSON file
geojson_file_path = "gadm41_THA_1.json"
with open(geojson_file_path, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Load the CSV files for province and district percentages
province_csv_path = "./Percentage_of_Correct_Predictions_by_Province.csv"
district_csv_path = "./Percentage_of_Correct_Predictions_by_Province_and_District.csv"
province_data = pd.read_csv(province_csv_path)
district_data = pd.read_csv(district_csv_path)

# Create dictionaries for quick lookup
province_percentage = province_data.set_index('province_input')['percentage_true'].to_dict()
district_percentage = district_data.set_index(['province_input', 'district_input'])['percentage_true'].to_dict()

# Create a Streamlit app
st.title("Thailand Provinces and Districts - Heatmap by Percentage")

# Initialize the map centered at Thailand
province_map = folium.Map(location=[13.736717, 100.523186], zoom_start=6)

# Add GeoJSON polygons with tooltips and percentage data for provinces
def get_tooltip_text_province(name):
    # Remove "จังหวัด" from NL_NAME_1 if present
    clean_name = name.replace("จังหวัด", "")
    percentage = province_percentage.get(clean_name, "N/A")  # Default to "N/A" if not found
    return f"{clean_name}: {percentage}%"

def get_color_province(percentage):
    # Assign colors based on percentage
    if percentage == "N/A":
        return "grey"
    percentage = float(percentage)
    if percentage > 75:
        return "green"
    elif percentage > 50:
        return "yellow"
    elif percentage > 25:
        return "orange"
    else:
        return "red"

for feature in geojson_data["features"]:
    name = feature["properties"]["NL_NAME_1"]  # Extract province name
    tooltip_text = get_tooltip_text_province(name)
    clean_name = name.replace("จังหวัด", "")
    percentage = province_percentage.get(clean_name, "N/A")
    color = get_color_province(percentage)
    folium.GeoJson(
        feature,
        tooltip=tooltip_text,  # Set the tooltip to display NAME_1 and percentage
        style_function=lambda x, color=color: {
            "fillColor": color,
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5,
        },
    ).add_to(province_map)

# Display the province map in Streamlit
st.subheader("Provinces Heatmap")
st_folium(province_map, width=800, height=600)

# Initialize the district map
district_map = folium.Map(location=[13.736717, 100.523186], zoom_start=6)

# Add GeoJSON polygons with tooltips and percentage data for districts
def get_tooltip_text_district(province, district):
    percentage = district_percentage.get((province, district), "N/A")  # Default to "N/A" if not found
    return f"{district}: {percentage}%"

for feature in geojson_data["features"]:
    province_name = feature["properties"]["NL_NAME_1"].replace("จังหวัด", "")
    for district in district_data[district_data['province_input'] == province_name]['district_input'].unique():
        tooltip_text = get_tooltip_text_district(province_name, district)
        folium.GeoJson(
            feature,
            tooltip=tooltip_text,  # Set the tooltip to display district name and percentage
            style_function=lambda x: {
                "fillColor": "blue",
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.5,
            },
        ).add_to(district_map)

# Display the district map in Streamlit
st.subheader("Districts Heatmap")
st_folium(district_map, width=800, height=600)
