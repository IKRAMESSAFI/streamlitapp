import streamlit as st
import rasterio
import geopandas as gpd
import folium
from folium import plugins
import matplotlib.pyplot as plt
from branca.colormap import LinearColormap
import numpy as np
import pandas as pd
import time

@st.cache_data(persist=True)
def load_data(path_to_geoparquet):
    return gpd.read_parquet(path_to_geoparquet)

def main():
    
    
    # Load the GeoParquet file
    path_to_geoparquet = "C:\\Users\\medam\\Downloads\\streamlit\\DONNEE_MAROC.parquet"
    gdf = load_data(path_to_geoparquet)
    
    # Afficher un message pendant le chargement des données
    with st.spinner("Chargement des données en cours ... veuillez patienter un peu..."):
        # Mettre en pause pendant 2 secondes pour simuler un chargement long
        time.sleep(4)
    
    # Convert the "Date" column to datetime format
    gdf['Date'] = pd.to_datetime(gdf['Date'])
    
    # Sidebar for attribute selection
    selected_attribute = st.sidebar.selectbox("Select attribute", [
        'Indice_Q_',
        'Taux_occ_',
        'Taux_plu_'
    ])
    
    # Slider to choose the day
    selected_day = st.sidebar.slider("Select day", 0, 6, 0)  # Moved to the sidebar
    
    # Check if the attribute column exists for the selected day
    selected_column_day = f'{selected_attribute}{selected_day}'
    
    if selected_column_day in gdf.columns:
        # Check if the selected column contains non-numeric values
        if not pd.api.types.is_numeric_dtype(gdf[selected_column_day].dtype):
            # You can optionally do something else instead of displaying the warning
            pass
        else:
            # Filter the data for the selected day
            filtered_data = gdf[gdf[selected_column_day] >= 0]
    
            # Create a grid for interpolation
            x_min, x_max, y_min, y_max = filtered_data.total_bounds
            x_res, y_res = 0.1, 0.1  # Adjust resolution as needed
            x_steps, y_steps = int((x_max - x_min) / x_res), int((y_max - y_min) / y_res)
    
            x_vals = np.linspace(x_min, x_max, x_steps)
            y_vals = np.linspace(y_min, y_max, y_steps)
    else:
        st.warning(f"Column '{selected_column_day}' not found in the GeoDataFrame.")
    
    # Load the raster corresponding to the selected attribute
    file_path = f"C:\\Users\\medam\\Downloads\\streamlit\\images\\{selected_attribute}{selected_day}.tif"
    
    # Function to read the GeoTIFF file with rasterio
    def read_geotiff(file_path):
        dataset = rasterio.open(file_path)
        return dataset
    
    # Function to convert the raster image to an image understandable by Streamlit
    def convert_to_streamlit_image(data):
        # Clamp values to the range [0.0, 1.0]
        clamped_data = np.clip(data, 0.0, 1.0)
        # Normalize values to the range [0.0, 1.0] using the inverse of the distance method
        normalized_data = 1 / (1 + clamped_data)
        return normalized_data
    
    # Function to get geospatial information
    def get_geospatial_info(dataset):
        bounds = dataset.bounds
        transform = dataset.transform
        return {
            "Bounds": [bounds[0], bounds[1], bounds[2], bounds[3]],
            "CRS": str(dataset.crs),
            "Transform": [transform[0], transform[1], transform[2], transform[3], transform[4], transform[5]],
        }
    
    # Function to create the basemap with Folium, add the raster layer with mask, and enable value display
    def create_folium_map_with_mask_and_mouse_position(raster_layer, geospatial_info):
        # Calculate the center of Morocco
        center_lat = (geospatial_info["Bounds"][1] + geospatial_info["Bounds"][3]) / 2
        center_lon = (geospatial_info["Bounds"][0] + geospatial_info["Bounds"][2]) / 2
    
        # Initialize the Folium map with the calculated center and appropriate zoom level
        m = folium.Map(location=[center_lat, center_lon], zoom_start=5)
    
        # Read raster data
        raster_data = raster_layer.read(1)
    
        # Create a mask for values not equal to 0
        mask = raster_data != 0
    
        # Apply the mask to the raster data
        raster_data_masked = np.ma.masked_where(~mask, raster_data)
    
        # Set the color range
        cmap = plt.get_cmap('cividis')  # You can choose another colormap
        norm = plt.Normalize(vmin=raster_data_masked.min(), vmax=raster_data_masked.max())
    
        # Define a function to determine vmin and vmax based on the selected attribute
        def get_attribute_range(attribute):
            if attribute == 'Indice_Q_':
                return 0, 100
            elif attribute == 'Taux_occ_':
                return 0, 20
            elif attribute == 'Taux_plu_':
                return 0, 50
            else:
                # Default values
                return 0, 100  # You can adjust the default values as needed
    
        # Set the color range based on the attribute
        vv_min, vv_max = get_attribute_range(selected_attribute)
    
        # Modify the next line to adjust the values displayed on the colormap
        num_classes = 10
        colormap = LinearColormap(
            colors=[cmap(norm(value)) for value in np.linspace(0, 255, num=num_classes)],
            vmin=vv_min,
            vmax=vv_max,
            caption=f'Legend Title - {selected_attribute}'  # Modify the legend title as needed
        )
    
        # Create a Matplotlib figure
        fig, ax = plt.subplots()
        img = ax.imshow(raster_data_masked, cmap=cmap, norm=norm)
    
        # Add the raster layer to the basemap with mask
        image_overlay = folium.raster_layers.ImageOverlay(
            image=img.to_rgba(raster_data_masked, bytes=True),
            bounds=[[geospatial_info["Bounds"][1], geospatial_info["Bounds"][0]],
                    [geospatial_info["Bounds"][3], geospatial_info["Bounds"][2]]],
            colormap=lambda x: colormap(x),
        )
        image_overlay.add_to(m)
    
        # Add legend with color bar
        colormap.add_to(m)
    
        # Add value display on cursor hover
        plugins.MousePosition().add_to(m)
    
        return m  # This line should be inside the create_folium_map_with_mask_and_mouse_position function
    
    st.title(" Slider permettant  possibilité de naviguer entre les cartes des différents attributs")
    
    # Read GeoTIFF file
    dataset = read_geotiff(file_path)
    
    # Get geospatial information
    geospatial_info = get_geospatial_info(dataset)
    
    # Create basemap with Folium, add raster layer with mask, and enable value display
    folium_map = create_folium_map_with_mask_and_mouse_position(dataset, geospatial_info)
    
    # Display basemap with Streamlit using st.components.v1.html
    st.write("Basemap with raster layer, mask, and value display:")
    st.components.v1.html(folium_map.get_root().render(), height=600)
    
    # Le message ci-dessous sera affiché après le chargement des données
    st.info("Chargement des données terminé. Vous pouvez maintenant explorer les données .")

# Call the main function
if __name__ == "__main__":
    main()
