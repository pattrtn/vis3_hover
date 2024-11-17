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

# Colormap selection for heatmap
colormap_option = st.sidebar.selectbox(
    "Select Colormap",
    ["RdYlBu", "YlGnBu", "Spectral", "viridis", "plasma", "cividis"]
)

# Convert the selected colormap to a matplotlib colormap object
cmap = plt.get_cmap(colormap_option)

# Dropdown for selecting a region (province or district)
region_type = st.selectbox("Select Region Type", ["Province", "District"])

# Initialize variables for selected province or district
selected_province = None
selected_district = None

# Dropdown for selecting a province
province_list = sorted([feature["properties"]["NAME_1"] for feature in geojson_data["features"]])
if region_type == "Province":
    selected_province = st.selectbox("Select a Province", ["All"] + province_list)

# Dropdown for selecting a district (only when "District" is selected in dropdown)
district_list = []
if region_type == "District" and selected_province:
    district_list = sorted(list(set(district_data[district_data['Province'] == selected_province]['district'])))
    selected_district = st.selectbox("Select a District", ["All"] + district_list)

# Initialize the map centered at Thailand
map_center = [13.736717, 100.523186]
zoom_level = 6
region_map = folium.Map(location=map_center, zoom_start=zoom_level)

# Filter GeoJSON data by selected region type
highlight_percentage = None
if region_type == "Province":
    if selected_province != "All":
        geojson_data["features"] = [
            feature for feature in geojson_data["features"]
            if feature["properties"]["NAME_1"] == selected_province
        ]
        highlight_percentage = province_percentage.get(selected_province.replace(' ', ''), 'N/A')
    else:
        geojson_data["features"] = geojson_data["features"]
elif region_type == "District":
    if selected_district != "All" and selected_province != "All":
        geojson_data2["features"] = [
            feature for feature in geojson_data2["features"]
            if feature["properties"]["NAME_1"] == selected_province and feature["properties"]["NAME_2"] == selected_district
        ]
        highlight_percentage = district_percentage.get((selected_province, selected_district), 'N/A')
    else:
        geojson_data2["features"] = geojson_data2["features"]

# Add the relevant polygons (for provinces or districts)
for feature in geojson_data["features"]:
    name = feature["properties"]["NAME_1"]
    percentage = province_percentage.get(name, "N/A")
    
    # Assign color based on the percentage
    if percentage == "N/A":
        color = "#D3D3D3"  # light grey for N/A
    else:
        color = cmap(percentage / 100)
    
    # Create GeoJson for the province with valid color
    geojson = folium.GeoJson(
        feature,
        tooltip=f"{name}: {percentage}%",
        style_function=lambda x, color=color: {
            "fillColor": mcolors.rgb2hex(color[:3]) if isinstance(color, tuple) else color,  # Use color if valid tuple
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5,
        }
    )
    geojson.add_to(region_map)

# Add the district polygons if district is selected
for feature in geojson_data2["features"]:
    province_name = feature["properties"]["NAME_1"]
    district_name = feature["properties"]["NAME_2"]
    percentage = district_percentage.get((province_name, district_name), "N/A")
    
    # Assign color based on the percentage
    if percentage == "N/A":
        color = "#D3D3D3"  # light grey for N/A
    else:
        color = cmap(percentage / 100)
    
    # Create GeoJson for the district with valid color
    folium.GeoJson(
        feature,
        tooltip=f"{district_name}: {percentage}%",
        style_function=lambda x, color=color: {
            "fillColor": mcolors.rgb2hex(color[:3]) if isinstance(color, tuple) else color,  # Use color if valid tuple
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5,
        }
    ).add_to(region_map)

# Display the combined map
st.subheader("Region Heatmap")
st_folium(region_map, width=800, height=600)

# Display the color scale in the sidebar based on selected region
if highlight_percentage != "N/A" and highlight_percentage is not None:
    plt.figure(figsize=(6, 0.5))
    gradient_array = np.linspace(0, 1, 256).reshape(1, -1)
    plt.imshow(gradient_array, aspect="auto", cmap=cmap)
    plt.axis("off")
    position = float(highlight_percentage) / 100 * 256  # Normalize percentage to 256-pixel width
    plt.bar([position], [1], color='black', width=5, align='center')  # Highlight position on the scale
    st.sidebar.pyplot(plt)
