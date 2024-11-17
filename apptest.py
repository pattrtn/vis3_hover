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

# Dropdown for selecting a province
province_list = sorted([feature["properties"]["NAME_1"] for feature in geojson_data["features"]])
selected_province = st.selectbox("Select a Province", ["All"] + province_list)

# Filter GeoJSON data by selected province
highlight_percentage = None
selected_district = None
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

# Dropdown for selecting a district (only when a province is selected)
district_list = sorted(list(set(district_data[district_data['Province'] == selected_province]['district'])))
selected_district = st.selectbox("Select a District", ["All"] + district_list)

# Initialize the map centered at Thailand
province_map = folium.Map(location=[13.736717, 100.523186], zoom_start=6)

# Add GeoJSON polygons with tooltips and percentage data for provinces
for feature in geojson_data["features"]:
    name = feature["properties"]["NAME_1"]  # Extract province name
    tooltip_text = f"{name}: {province_percentage.get(name, 'N/A')}%"
    percentage = province_percentage.get(name, "N/A")
    
    # Determine the color based on the colormap
    if percentage == "N/A":
        color = "grey"
    else:
        color = cmap(percentage / 100)  # Normalize the percentage to [0, 1] range

    geojson = folium.GeoJson(
        feature,
        tooltip=tooltip_text,  # Set the tooltip to display NAME_1 and percentage
        style_function=lambda x, color=color: {
            "fillColor": mcolors.rgb2hex(color[:3]) if isinstance(color, tuple) else "grey",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5,
        }
    )
    geojson.add_child(
        folium.Popup(f"Province: {name}<br>Percentage: {percentage}%")
    )
    geojson.add_to(province_map)

# Display the province map in Streamlit
st.subheader("Provinces Heatmap")
province_map_data = st_folium(province_map, width=800, height=600)

# Highlight position on gradient if a province or district is selected
if selected_province != "All":
    # Show province-specific percentage
    if highlight_percentage != "N/A" and highlight_percentage is not None:
        st.sidebar.subheader(f"Percentage for {selected_province}: {highlight_percentage}%")
        # Display the color scale indicating the value for the selected province
        position = float(highlight_percentage) / 100 * 256  # Normalize percentage to 256-pixel width
        plt.figure(figsize=(6, 0.5))
        gradient_array = np.linspace(0, 1, 256).reshape(1, -1)
        plt.imshow(gradient_array, aspect="auto", cmap=cmap)
        plt.axis("off")
        plt.bar([position], [1], color='black', width=5, align='center')  # Highlight the position on the color bar
        st.sidebar.pyplot(plt)

# Initialize the district map if a district is selected
district_map = folium.Map(location=[13.736717, 100.523186], zoom_start=6)

# Add GeoJSON polygons with tooltips and percentage data for districts
if selected_district != "All":
    for feature in geojson_data2["features"]:
        province_name = feature["properties"]["NAME_1"]
        district_name = feature["properties"]["NAME_2"]
        
        # Only add district polygons if it matches the selected district
        if province_name == selected_province and district_name == selected_district:
            percentage = district_percentage.get((province_name, district_name), "N/A")
            tooltip_text = f"{district_name}: {percentage}%"
            
            # Determine the color based on the colormap
            if percentage == "N/A":
                color = "grey"
            else:
                color = cmap(percentage / 100)  # Normalize the percentage to [0, 1] range

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
    st_folium(district_map, width=800, height=600)

    # Highlight position on gradient if a district is selected
    if selected_district != "All":
        district_percentage_value = district_percentage.get((selected_province, selected_district), "N/A")
        if district_percentage_value != "N/A":
            st.sidebar.subheader(f"Percentage for {selected_district} in {selected_province}: {district_percentage_value}%")
            position = float(district_percentage_value) / 100 * 256  # Normalize percentage to 256-pixel width
            plt.figure(figsize=(6, 0.5))
            gradient_array = np.linspace(0, 1, 256).reshape(1, -1)
            plt.imshow(gradient_array, aspect="auto", cmap=cmap)
            plt.axis("off")
            plt.bar([position], [1], color='black', width=5, align='center')  # Highlight the position on the color bar
            st.sidebar.pyplot(plt)

