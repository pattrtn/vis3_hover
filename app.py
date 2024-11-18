import json
import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Load the GeoJSON files
geojson_file_path = "gadm41_THA_1.json"  # Provinces GeoJSON file
with open(geojson_file_path, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

geojson_file_path2 = "gadm41_THA_2.json"  # Districts GeoJSON file
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

# Streamlit App
st.title("Thailand Provinces and Districts - Heatmap by Accuracy Percentage")
st.markdown("[Predict Form](https://vis3test-frevdr8gq4bj582g7urhhv.streamlit.app/)!")

st.markdown(
    """This heatmap visualizes the accuracy percentage of data across Thailand’s provinces and districts. 
    Each region is color-coded based on the accuracy of the information associated with it, providing a clear and intuitive way to assess the quality of data at both the provincial and district levels."""
)

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
district_list = sorted(list(set(district_data[district_data['Province'] == selected_province]['district'].astype(str))))
selected_district = st.selectbox("Select a District", ["All"] + district_list)

# Function to create and add district data to the map (only for the selected district or all districts)
def create_district_map():
    # Create a new folium map each time the function is called
    district_map = folium.Map(location=[13.736717, 100.523186], zoom_start=6)
    
    for feature in geojson_data2["features"]:
        province_name = feature["properties"]["NAME_1"]
        district_name = feature["properties"]["NAME_2"]

        # Add all districts or only the selected district
        if selected_district != "All" and district_name != selected_district:
            continue
        
        # Get the percentage for this district
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
    
    return district_map

# Function to create and add province data to the map (only for the selected province or all provinces)
def create_province_map():
    # Create a new folium map for provinces
    province_map = folium.Map(location=[13.736717, 100.523186], zoom_start=6)
    
    for feature in geojson_data["features"]:
        province_name = feature["properties"]["NAME_1"]
        # If we are showing all provinces, don't filter out anything
        if selected_province == "All" or province_name == selected_province:
            # Get the percentage for this province
            percentage = province_percentage.get(province_name, "N/A")
            tooltip_text = f"{province_name}: {percentage}%"
            
            # Determine the color based on the colormap
            if percentage == "N/A":
                color = "grey"
            else:
                color = cmap(percentage / 100)

            folium.GeoJson(
                feature,
                tooltip=tooltip_text,  # Set the tooltip to display province name and percentage
                style_function=lambda x, color=color: {
                    "fillColor": mcolors.rgb2hex(color[:3]) if isinstance(color, tuple) else "grey",
                    "color": "black",
                    "weight": 1,
                    "fillOpacity": 0.5,
                }
            ).add_to(province_map)
    
    return province_map

# Display separate maps based on selection
if selected_province != "All":
    # Display the province heatmap when a province is selected
    st.subheader(f"Province Heatmap for {selected_province}")
    province_map = create_province_map()
    st_folium(province_map, width=800, height=600)
    
    # Show the percentage for the selected province in the sidebar
    st.sidebar.subheader(f"Percentage for {selected_province}: {highlight_percentage}%")

    # Color scale for province selection
    position = float(highlight_percentage) / 100 * 256  # Normalize percentage to 256-pixel width
    plt.figure(figsize=(6, 0.5))
    gradient_array = np.linspace(0, 1, 256).reshape(1, -1)
    plt.imshow(gradient_array, aspect="auto", cmap=cmap)
    plt.axis("off")
    plt.bar([position], [1], color='black', width=5, align='center')  # Highlight the position on the color bar
    st.sidebar.subheader("Province Color Scale")  # Title for Province color scale
    st.sidebar.pyplot(plt)

elif selected_province == "All":
    # Display all provinces heatmap when "All" is selected for province
    st.subheader("All Provinces Heatmap")
    province_map = create_province_map()
    st_folium(province_map, width=800, height=600)

if selected_district != "All":
    # Display the district heatmap when a district is selected
    st.subheader(f"District Heatmap for {selected_district} in {selected_province}")
    district_map = create_district_map()
    st_folium(district_map, width=800, height=600)

elif selected_district == "All" and selected_province != "All":
    # Display all districts of the selected province heatmap
    st.subheader(f"All Districts in {selected_province} Heatmap")
    district_map = create_district_map()
    st_folium(district_map, width=800, height=600)

# Color scale for district selection
district_percentage_value = None
if selected_district != "All":
    district_percentage_value = district_percentage.get((selected_province, selected_district), "N/A")
    if district_percentage_value != "N/A":
        # Show the percentage of the selected district
        st.sidebar.subheader(f"Percentage for {selected_district} in {selected_province}: {district_percentage_value}%")
        
        # Update the map color for the selected district
        for feature in geojson_data2["features"]:
            province_name = feature["properties"]["NAME_1"]
            district_name = feature["properties"]["NAME_2"]
            if province_name == selected_province and district_name == selected_district:
                percentage = district_percentage.get((province_name, district_name), "N/A")
                color = cmap(percentage / 100)  # Normalize percentage
                folium.GeoJson(
                    feature,
                    tooltip=f"{district_name}: {percentage}%",
                    style_function=lambda x, color=color: {
                        "fillColor": mcolors.rgb2hex(color[:3]),
                        "color": "black",
                        "weight": 1,
                        "fillOpacity": 0.7,
                    }
                ).add_to(district_map)

# Color scale for district selection
if selected_district != "All" and district_percentage_value != "N/A":
    position = float(district_percentage_value) / 100 * 256  # Normalize percentage to 256-pixel width
    plt.figure(figsize=(6, 0.5))
    gradient_array = np.linspace(0, 1, 256).reshape(1, -1)
    plt.imshow(gradient_array, aspect="auto", cmap=cmap)
    plt.axis("off")
    plt.bar([position], [1], color='black', width=5, align='center')  # Highlight the position on the color bar
    st.sidebar.subheader("District Color Scale")  # Title for District color scale
    st.sidebar.pyplot(plt)
