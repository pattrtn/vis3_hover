import json
import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Load the GeoJSON file
geojson_file_path = "gadm41_THA_1.json"
with open(geojson_file_path, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

geojson_file_path2 = "gadm41_THA_2.json"
with open(geojson_file_path2, "r", encoding="utf-8") as f2:
    geojson_data2 = json.load(f2)

# Load the CSV files for province and district percentages
province_csv_path = "./Province_Check_Percentage.csv"
district_csv_path = "./Province_and_District_Check_Percentage.csv"
province_data = pd.read_csv(province_csv_path)
district_data = pd.read_csv(district_csv_path)

# Remove whitespace from province and district names
province_data['Province'] = province_data['Province'].str.replace(' ', '').replace('Bangkok', 'BangkokMetropolis')
district_data['Province'] = district_data['Province'].str.replace(' ', '').replace('Bangkok', 'BangkokMetropolis')
district_data['district'] = district_data['district'].str.replace(' ', '')

# Create dictionaries for quick lookup
province_percentage = province_data.set_index('Province')['percentage_true'].to_dict()
district_percentage = district_data.set_index(['Province', 'district'])['percentage_true'].to_dict()

# Create a Streamlit app
st.title("Thailand Provinces and Districts - Heatmap by Percentage")

# Sidebar for data range visualization
st.sidebar.header("Data Range")
min_percentage = min(province_data['percentage_true'].min(), district_data['percentage_true'].min())
max_percentage = max(province_data['percentage_true'].max(), district_data['percentage_true'].max())
st.sidebar.markdown(f"**Low**: {min_percentage}%")
st.sidebar.markdown(f"**High**: {max_percentage}%")
st.sidebar.color_picker("Color Range", "#FF0000")

# Dropdown for selecting a province
province_list = sorted([feature["properties"]["NAME_1"] for feature in geojson_data["features"]])
selected_province = st.selectbox("Select a Province", ["All"] + province_list)

# Filter GeoJSON data by selected province
if selected_province != "All":
    geojson_data["features"] = [
        feature for feature in geojson_data["features"]
        if feature["properties"]["NAME_1"] == selected_province
    ]
    geojson_data2["features"] = [
        feature for feature in geojson_data2["features"]
        if feature["properties"]["NAME_1"] == selected_province
    ]
    district_data = district_data[district_data['Province'] == selected_province.replace(' ', '')]

# Initialize the map centered at Thailand
province_map = folium.Map(location=[13.736717, 100.523186], zoom_start=6)

# Add GeoJSON polygons with tooltips and percentage data for provinces
def get_tooltip_text_province(name):
    percentage = province_percentage.get(name, "N/A")  # Default to "N/A" if not found
    return f"{name}: {percentage}%"

def get_color_province(percentage):
    if percentage == "N/A":
        return "grey"
    
    # Convert percentage to float and normalize
    percentage = float(percentage)
    normalized_percentage = np.clip(percentage / 100, 0, 1)

    # Use matplotlib's 'Reds' colormap (from white to red)
    cmap = plt.get_cmap("RdYlBu")
    rgba_color = cmap(normalized_percentage)
    
    # Convert the RGBA color to hex
    hex_color = mcolors.rgb2hex(rgba_color[:3])
    return hex_color

for feature in geojson_data["features"]:
    name = feature["properties"]["NAME_1"]  # Extract province name
    tooltip_text = get_tooltip_text_province(name)
    percentage = province_percentage.get(name, "N/A")
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
for feature in geojson_data2["features"]:
    province_name = feature["properties"]["NAME_1"]
    district_name = feature["properties"]["NAME_2"]
    percentage = district_percentage.get((province_name, district_name), "N/A")
    tooltip_text = f"{district_name}: {percentage}%"
    color = get_color_province(percentage)
    folium.GeoJson(
        feature,
        tooltip=tooltip_text,  # Set the tooltip to display district name and percentage
        style_function=lambda x, color=color: {
            "fillColor": color,
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5,
        },
    ).add_to(district_map)

# Display the district map in Streamlit
st.subheader("Districts Heatmap")
st_folium(district_map, width=800, height=600)


# Handle user interaction with provinces
if province_map_data and 'last_active_drawing' in province_map_data:
    clicked_province = province_map_data['last_active_drawing']
    if clicked_province and 'properties' in clicked_province:
        selected_province_name = clicked_province['properties'].get('NAME_1', 'Unknown')
        highlight_percentage = province_percentage.get(selected_province_name, 'N/A')

        # Update selected province dropdown in sidebar
        selected_province = st.sidebar.selectbox("Select a Province", 
                                                 ["All"] + province_list, 
                                                 index=province_list.index(selected_province_name) 
                                                 if selected_province_name in province_list else 0)

        st.sidebar.markdown(f"**Selected Province**: {selected_province_name}")
        st.sidebar.markdown(f"**Percentage**: {highlight_percentage}%")
