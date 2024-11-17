import json
import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Load the GeoJSON files for Thailand's provinces and districts
geojson_file_path = "gadm41_THA_1.json"
with open(geojson_file_path, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

geojson_file_path2 = "gadm41_THA_2.json"
with open(geojson_file_path2, "r", encoding="utf-8") as f2:
    geojson_data2 = json.load(f2)

# Load CSV files for percentage data
province_csv_path = "./Province_Check_Percentage.csv"
district_csv_path = "./Province_and_District_Check_Percentage.csv"
province_data = pd.read_csv(province_csv_path)
district_data = pd.read_csv(district_csv_path)

# Clean and preprocess the data
province_data['Province'] = province_data['Province'].str.replace(' ', '').replace('Bangkok', 'BangkokMetropolis')
district_data['Province'] = district_data['Province'].str.replace(' ', '').replace('Bangkok', 'BangkokMetropolis')
district_data['district'] = district_data['district'].str.replace(' ', '')

# Create dictionaries for quick lookup
province_percentage = province_data.set_index('Province')['percentage_true'].to_dict()
district_percentage = district_data.set_index(['Province', 'district'])['percentage_true'].to_dict()

# Streamlit app title and description
st.title("Thailand Provinces and Districts - Heatmap by Accuracy Percentage")
st.markdown("[Prediction Form](https://vis3test-frevdr8gq4bj582g7urhhv.streamlit.app/) !")
st.markdown("""
    This heatmap visualizes the accuracy percentage of data across Thailand’s provinces and districts. 
    Each region is color-coded based on the accuracy of the information associated with it, providing a clear and intuitive way to assess the quality of data at both the provincial and district levels.
""")

# Sidebar for colormap selection and data range
st.sidebar.header("Data Range")
min_percentage = 0  # Gradient starts at 0%
max_percentage = 100  # Gradient ends at 100%
st.sidebar.markdown(f"**Low**: {min_percentage}%")
st.sidebar.markdown(f"**High**: {max_percentage}%")

colormap_option = st.sidebar.selectbox(
    "Select Colormap",
    ["RdYlBu", "YlGnBu", "Spectral", "viridis", "plasma", "cividis"]
)

# Gradient color map based on the selected option
cmap = plt.get_cmap(colormap_option)

# Dropdown for selecting a province
province_list = sorted([feature["properties"]["NAME_1"] for feature in geojson_data["features"]])
selected_province = st.selectbox("Select a Province", ["All"] + province_list)

# Filter GeoJSON data by selected province
highlight_percentage = None
if selected_province != "All":
    geojson_data["features"] = [
        feature for feature in geojson_data["features"]
        if feature["properties"]["NAME_1"] == selected_province
    ]
    geojson_data2["features"] = [
        feature for feature in geojson_data2["features"]
        if feature["properties"]["NAME_1"] == selected_province
    ]
    highlight_percentage = province_percentage.get(selected_province.replace(' ', ''), 'N/A')

# Create and display the province map
province_map = folium.Map(location=[13.736717, 100.523186], zoom_start=6)

# Add GeoJSON polygons with tooltips for provinces
for feature in geojson_data["features"]:
    name = feature["properties"]["NAME_1"]
    percentage = province_percentage.get(name, "N/A")
    color = "grey" if percentage == "N/A" else cmap(percentage / 100)  # Apply colormap

    folium.GeoJson(
        feature,
        tooltip=f"{name}: {percentage}%",
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

# Sidebar gradient visualization
if highlight_percentage != "N/A" and highlight_percentage is not None:
    st.sidebar.markdown(f"**Highlight Percentage (Selected Province):** {highlight_percentage}%")
    plt.figure(figsize=(6, 1))
    gradient_array = np.linspace(0, 1, 256).reshape(1, -1)
    plt.imshow(gradient_array, aspect="auto", cmap=cmap)
    plt.xlabel("Percentage (0-100)")
    plt.ylabel("Intensity")
    position = float(highlight_percentage) / 100 * 256  # Normalize percentage to 256-pixel width
    plt.bar([position], [1], color='black', width=5, align='center')
    st.sidebar.pyplot(plt)

# Add Dropdown to select district
district_list = sorted(list(set(district_data['district'])))
selected_district = st.selectbox("Select a District", ["All"] + district_list)

# Initialize the district map
district_map = folium.Map(location=[13.736717, 100.523186], zoom_start=6)

# Filter GeoJSON data by selected district (if any)
if selected_district != "All":
    geojson_data2["features"] = [
        feature for feature in geojson_data2["features"]
        if feature["properties"]["NAME_2"] == selected_district
    ]

# Add GeoJSON polygons for districts to the map
for feature in geojson_data2["features"]:
    province_name = feature["properties"]["NAME_1"]
    district_name = feature["properties"]["NAME_2"]
    percentage = district_percentage.get((province_name, district_name), "N/A")
    color = "grey" if percentage == "N/A" else cmap(percentage / 100)  # Apply colormap
    folium.GeoJson(
        feature,
        tooltip=f"{district_name}: {percentage}%",
        style_function=lambda x, color=color: {
            "fillColor": mcolors.rgb2hex(color[:3]) if isinstance(color, tuple) else "grey",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5,
        }
    ).add_to(district_map)

# Display the district map in Streamlit
st.subheader("Districts Heatmap")
st_folium(district_map, width=800, height=600)
