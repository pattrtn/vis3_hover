import json
import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Load the GeoJSON files
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
st.sidebar.markdown("### Gradient Map")
min_percentage = 0  # Gradient starts at 0%
max_percentage = 100  # Gradient ends at 100%
st.sidebar.markdown(f"**Low**: {min_percentage}%")
st.sidebar.markdown(f"**High**: {max_percentage}%")

# Add a selectbox for the user to choose a color map
colormap_option = st.sidebar.selectbox(
    "Select Colormap",
    ["RdYlBu", "YlGnBu", "Spectral", "viridis", "plasma", "cividis"]
)

# Use the selected colormap
cmap = plt.get_cmap(colormap_option)

# Add a title for the province scale in the sidebar
st.sidebar.markdown("### Province Scale")

# Dropdown for selecting a province
province_list = sorted([feature["properties"]["NAME_1"] for feature in geojson_data["features"]])
selected_province = st.selectbox("Select a Province", ["All"] + province_list)

# Filter GeoJSON data by selected province
highlight_percentage = None
district_list = []
if selected_province != "All":
    # Filter only the selected province's features from the GeoJSON data
    geojson_data["features"] = [
        feature for feature in geojson_data["features"]
        if feature["properties"]["NAME_1"] == selected_province
    ]
    geojson_data2["features"] = [
        feature for feature in geojson_data2["features"]
        if feature["properties"]["NAME_1"] == selected_province
    ]
    
    # Collect list of districts for the selected province
    district_list = sorted(set([feature["properties"]["NAME_2"] for feature in geojson_data2["features"] if feature["properties"]["NAME_1"] == selected_province]))

    highlight_percentage = province_percentage.get(selected_province.replace(' ', ''), 'N/A')
    st.write("Highlight Percentage (Selected Province):", highlight_percentage)

# Dropdown for selecting a district, only show when a province is selected
district_selected = None
if district_list:
    district_selected = st.selectbox("Select a District", ["None"] + district_list)

# Initialize the map centered at Thailand
province_map = folium.Map(location=[13.736717, 100.523186], zoom_start=6)

# Add GeoJSON polygons with tooltips and percentage data for provinces
for feature in geojson_data["features"]:
    name = feature["properties"]["NAME_1"]  # Extract province name
    tooltip_text = f"{name}: {province_percentage.get(name, 'N/A')}%"
    percentage = province_percentage.get(name, "N/A")
    color = "grey" if percentage == "N/A" else cmap(percentage / 100)  # Use the selected colormap
    
    folium.GeoJson(
        feature,
        tooltip=tooltip_text,  # Set the tooltip to display NAME_1 and percentage
        style_function=lambda x, color=color: {
            "fillColor": mcolors.rgb2hex(color[:3]) if isinstance(color, tuple) else "grey",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5,
        }
    ).add_to(province_map)

# Display the province map in Streamlit
st.subheader("Provinces Heatmap")
province_map_data = st_folium(province_map, width=800, height=600)

# Handle user interaction with provinces
if province_map_data and 'last_active_drawing' in province_map_data:
    clicked_province = province_map_data['last_active_drawing']
    if clicked_province:
        selected_province_name = clicked_province.get('properties', {}).get('NAME_1', 'Unknown')
        highlight_percentage = province_percentage.get(selected_province_name.replace(' ', ''), 'N/A')
        st.sidebar.markdown(f"**Clicked Province**: {selected_province_name}")
        st.sidebar.markdown(f"**Percentage**: {highlight_percentage}%")

# **District Selection**
district_percentage_value = "N/A"
if district_selected and district_selected != "None":
    # Get the percentage for the selected district
    district_percentage_value = district_percentage.get((selected_province, district_selected), "N/A")

# Initialize the district map
district_map = folium.Map(location=[13.736717, 100.523186], zoom_start=6)

# Add GeoJSON polygons with tooltips and percentage data for districts
for feature in geojson_data2["features"]:
    province_name = feature["properties"]["NAME_1"]
    district_name = feature["properties"]["NAME_2"]
    percentage = district_percentage.get((province_name, district_name), "N/A")
    tooltip_text = f"{district_name}: {percentage}%"
    color = "grey" if percentage == "N/A" else cmap(percentage / 100)  # Use the selected colormap
    
    folium.GeoJson(
        feature,
        tooltip=tooltip_text,  # Set the tooltip to display district name and percentage
        style_function=lambda x, color=color: {
            "fillColor": mcolors.rgb2hex(color[:3]) if isinstance(color, tuple) else "grey",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5,
        }
    ).add_to(district_map)

# Display the district map in Streamlit
st.subheader("Districts Heatmap")
district_map_data = st_folium(district_map, width=800, height=600)

# Handle user interaction with districts
if district_map_data and 'last_active_drawing' in district_map_data:
    clicked_district = district_map_data['last_active_drawing']
    if clicked_district:
        clicked_province_name = clicked_district.get('properties', {}).get('NAME_1', 'Unknown')
        clicked_district_name = clicked_district.get('properties', {}).get('NAME_2', 'Unknown')
        district_percentage_value = district_percentage.get((clicked_province_name, clicked_district_name), 'N/A')
        st.sidebar.markdown(f"**Clicked Province**: {clicked_province_name}")
        st.sidebar.markdown(f"**Clicked District**: {clicked_district_name}")
        st.sidebar.markdown(f"**District Percentage**: {district_percentage_value}%")

# Highlight position on gradient for district if selected
if district_percentage_value != "N/A" and district_percentage_value is not None:
    plt.figure(figsize=(6, 1))
    gradient_array = np.linspace(0, 1, 256).reshape(1, -1)
    plt.imshow(gradient_array, aspect="auto", cmap=cmap)
    plt.xlabel("Percentage (0-100)")
    plt.ylabel("Intensity")
    position = float(district_percentage_value) / 100 * 256  # Normalize percentage to 256-pixel width
    plt.bar([position], [1], color='black', width=5, align='center')
    st.sidebar.pyplot(plt)

# Show the province gradient scale in the sidebar
if selected_province != "All":
    st.sidebar.markdown("### Province Scale")
    plt.figure(figsize=(6, 1))
    gradient_array = np.linspace(0, 1, 256).reshape(1, -1)
    plt.imshow(gradient_array, aspect="auto", cmap=cmap)
    plt.xlabel("Percentage (0-100)")
    plt.ylabel("Intensity")
    position = float(highlight_percentage) / 100 * 256  # Normalize province percentage
    plt.bar([position], [1], color='black', width=5, align='center')
    st.sidebar.pyplot(plt)
