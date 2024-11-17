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
colormap_option = st.sidebar.selectbox(
    "Select Colormap", ["RdYlBu", "YlGnBu", "Spectral", "viridis", "plasma", "cividis"]
)
cmap = plt.get_cmap(colormap_option)

# Dropdown for selecting a province
province_list = sorted([feature["properties"]["NAME_1"] for feature in geojson_data["features"]])
selected_province = st.selectbox("Select a Province", ["All"] + province_list)

# Dropdown for selecting a district (only when a province is selected)
district_list = sorted(list(set(district_data[district_data['Province'] == selected_province]['district'])))
selected_district = st.selectbox("Select a District", ["All"] + district_list)

# Initialize the map centered at Thailand
map_center = [13.736717, 100.523186]  # Coordinates for Thailand
district_map = folium.Map(location=map_center, zoom_start=6)

# Define function to create gradient scale
def show_gradient(scale_type="province"):
    gradient_array = np.linspace(0, 1, 256).reshape(1, -1)
    plt.figure(figsize=(6, 0.5))
    if scale_type == "province":
        plt.imshow(gradient_array, aspect="auto", cmap=cmap)
        plt.title(f"Province Gradient: {min_percentage}% - {max_percentage}%")
    elif scale_type == "district":
        plt.imshow(gradient_array, aspect="auto", cmap=cmap)
        plt.title(f"District Gradient: {min_percentage}% - {max_percentage}%")
    plt.axis("off")
    st.sidebar.pyplot(plt)

# Show appropriate gradient scale
if selected_province != "All" and selected_district == "All":
    show_gradient(scale_type="province")
elif selected_district != "All":
    show_gradient(scale_type="district")
else:
    # No specific province or district selected, hide scale
    pass

# Add GeoJSON polygons with tooltips and percentage data for all districts or provinces
for feature in geojson_data2["features"]:
    province_name = feature["properties"]["NAME_1"]
    district_name = feature["properties"]["NAME_2"]
    
    if selected_province != "All" and selected_district == "All":
        # Province map visualization
        percentage = province_percentage.get(province_name, "N/A")
        tooltip_text = f"{province_name}: {percentage}%" if percentage != "N/A" else f"{province_name}: N/A"
        color = cmap(percentage / 100) if percentage != "N/A" else "grey"
    elif selected_province != "All" and selected_district != "All" and province_name == selected_province and district_name == selected_district:
        # District map visualization for the selected district
        percentage = district_percentage.get((province_name, district_name), "N/A")
        tooltip_text = f"{district_name}: {percentage}%" if percentage != "N/A" else f"{district_name}: N/A"
        color = cmap(percentage / 100) if percentage != "N/A" else "grey"
    else:
        continue  # Skip if it doesn't match the selected filters

    folium.GeoJson(
        feature,
        tooltip=tooltip_text,
        style_function=lambda x, color=color: {
            "fillColor": mcolors.rgb2hex(color[:3]) if isinstance(color, tuple) else "grey",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5,
        }
    ).add_to(district_map)

# Display the map in Streamlit
st.subheader("Districts/Provinces Heatmap")
st_folium(district_map, width=800, height=600)
