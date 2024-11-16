import json
import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd

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

# Add GeoJSON polygons with tooltips and percentage data for provinces
def get_tooltip_text_province(name):
    # Remove "จังหวัด" from NL_NAME_1 if present
    clean_name = name.replace("จังหวัด", "")
    percentage = province_percentage.get(clean_name, "N/A")  # Default to "N/A" if not found
    return f"{clean_name}: {percentage}%"

# def get_color_province(percentage):
#     # Assign colors based on percentage
#     if percentage == "N/A":
#         return "grey"
#     percentage = float(percentage)
#     if percentage > 75:
#         return "green"
#     elif percentage > 50:
#         return "yellow"
#     elif percentage > 25:
#         return "orange"
#     else:
#         return "red"
def get_color_province(percentage):
    # Handle "N/A" case
    if percentage == "N/A":
        return "grey"

    # Convert the percentage to a float
    percentage = float(percentage)

    # Normalize the percentage to a value between 0 and 1
    normalized_percentage = np.clip(percentage / 100, 0, 1)

    # Use matplotlib's 'coolwarm' colormap (blue-to-red)
    cmap = plt.get_cmap("coolwarm")
    
    # Get the corresponding color from the colormap
    rgba_color = cmap(normalized_percentage)

    # Convert the RGBA color to a hex color code
    hex_color = matplotlib.colors.rgb2hex(rgba_color[:3])

    return hex_color

for feature in geojson_data_1["features"]:
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
    ).add_to(map_1)

# Display the first map in Streamlit
st.subheader("Provinces Heatmap")
st_folium(map_1, width=800, height=600)

# Initialize the second map for districts
map_2 = folium.Map(location=[13.736717, 100.523186], zoom_start=6)

# Add GeoJSON polygons with tooltips for districts
def get_tooltip_text_district(name):
    # Remove "อำเภอ" or similar prefixes from NL_NAME_2 if present
    clean_name = name.replace("อำเภอ", "")
    return clean_name

for feature in geojson_data_2["features"]:
    name = feature["properties"]["NL_NAME_2"]  # Extract district name
    tooltip_text = get_tooltip_text_district(name)
    folium.GeoJson(
        feature,
        tooltip=tooltip_text,  # Set the tooltip to display NL_NAME_2
        style_function=lambda x: {
            "fillColor": "blue",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5,
        },
    ).add_to(map_2)

# Display the second map in Streamlit
st.subheader("Districts Map")
st_folium(map_2, width=800, height=600)
