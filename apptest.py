# Function to add districts to the map (or only the selected district)
def add_districts_to_map(selected_province, selected_district):
    # Initialize the district map again to reset the display
    district_map = folium.Map(location=[13.736717, 100.523186], zoom_start=6)
    
    if selected_district != "All":
        # Only show the selected district
        for feature in geojson_data2["features"]:
            province_name = feature["properties"]["NAME_1"]
            district_name = feature["properties"]["NAME_2"]
            
            if province_name == selected_province and district_name == selected_district:
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
    else:
        # Show all districts if "All" is selected
        for feature in geojson_data2["features"]:
            province_name = feature["properties"]["NAME_1"]
            district_name = feature["properties"]["NAME_2"]
            
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

# Streamlit code for handling map updates based on district selection
district_map = add_districts_to_map(selected_province, selected_district)

# Show the updated map
st.subheader("Districts Heatmap")
district_map_data = st_folium(district_map, width=800, height=600)
