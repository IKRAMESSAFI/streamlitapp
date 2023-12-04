import streamlit as st
import geopandas as gpd
import folium
from folium import plugins
from branca.colormap import LinearColormap
import rasterio
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
from cogeo_mosaic.mosaic import MosaicJSON

# Function to load GeoParquet data
@st.cache_data(persist=True)
def load_data(path_to_geoparquet):
    return gpd.read_parquet(path_to_geoparquet)

# Function to read GeoTIFF file with rasterio
def read_geotiff(file_path, comment):  # Added 'comment' parameter
    start_time = time.time()
    dataset = rasterio.open(file_path)
    end_time = time.time()
    st.sidebar.text(f"{comment} GeoTIFF Loaded in: {end_time - start_time:.2f} seconds")
    return dataset

# Function to get geospatial information
def get_geospatial_info(dataset):
    bounds = dataset.bounds
    transform = dataset.transform
    return {
        "Bounds": [bounds[0], bounds[1], bounds[2], bounds[3]],
        "CRS": str(dataset.crs),
        "Transform": [transform[0], transform[1], transform[2], transform[3], transform[4], transform[5]],
    }

# Function to create Folium map with mask and mouse position for GeoTIFF
def create_geotiff_folium_map_with_mask_and_mouse_position(raster_layer, geospatial_info, selected_attribute, zoom_level=5):
    start_time = time.time()

    center_lat = (geospatial_info["Bounds"][1] + geospatial_info["Bounds"][3]) / 2
    center_lon = (geospatial_info["Bounds"][0] + geospatial_info["Bounds"][2]) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level)

    raster_data = raster_layer.read(1)
    mask = raster_data != 0
    raster_data_masked = np.ma.masked_where(~mask, raster_data)

    cmap = plt.get_cmap('cividis')
    norm = plt.Normalize(vmin=raster_data_masked.min(), vmax=raster_data_masked.max())

    def get_attribute_range(attribute):
        if attribute == 'Indice_Q_':
            return 0, 100
        elif attribute == 'Taux_occ_':
            return 0, 20
        elif attribute == 'Taux_plu_':
            return 0, 50
        else:
            return 0, 100

    vv_min, vv_max = get_attribute_range(selected_attribute)

    num_classes = 10
    colormap = LinearColormap(
        colors=[cmap(norm(value)) for value in np.linspace(0, 255, num=num_classes)],
        vmin=vv_min,
        vmax=vv_max,
        caption=f'Legend Title - {selected_attribute}'
    )

    fig, ax = plt.subplots()
    img = ax.imshow(raster_data_masked, cmap=cmap, norm=norm)

    image_overlay = folium.raster_layers.ImageOverlay(
        image=img.to_rgba(raster_data_masked, bytes=True),
        bounds=[[geospatial_info["Bounds"][1], geospatial_info["Bounds"][0]],
                [geospatial_info["Bounds"][3], geospatial_info["Bounds"][2]]],
        colormap=lambda x: colormap(x),
    )
    image_overlay.add_to(m)

    colormap.add_to(m)

    plugins.MousePosition().add_to(m)

    # Add a label indicating GeoTIFF
    folium.Marker(location=[center_lat, center_lon], icon=folium.DivIcon(icon_size=(150,36), icon_anchor=(0,0),
              html=f'<div style="font-size: 12pt; color : red;">GeoTIFF</div>')).add_to(m)

    end_time = time.time()
    st.sidebar.text(f"Folium Map Created in: {end_time - start_time:.2f} seconds (GeoTIFF)")

    return m
# Function to create Folium map with mask and mouse position for COG
def create_folium_map_with_mask_and_mouse_position(raster_layer, geospatial_info, selected_attribute, zoom_level=5):
    start_time = time.time()

    center_lat = (geospatial_info["Bounds"][1] + geospatial_info["Bounds"][3]) / 2
    center_lon = (geospatial_info["Bounds"][0] + geospatial_info["Bounds"][2]) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level)

    raster_data = raster_layer.read(1)
    mask = raster_data != 0
    raster_data_masked = np.ma.masked_where(~mask, raster_data)

    cmap = plt.get_cmap('cividis')
    norm = plt.Normalize(vmin=raster_data_masked.min(), vmax=raster_data_masked.max())

    def get_attribute_range(attribute):
        if attribute == 'Indice_Q_':
            return 0, 100
        elif attribute == 'Taux_occ_':
            return 0, 20
        elif attribute == 'Taux_plu_':
            return 0, 50
        else:
            return 0, 100

    vv_min, vv_max = get_attribute_range(selected_attribute)

    num_classes = 10
    colormap = LinearColormap(
        colors=[cmap(norm(value)) for value in np.linspace(0, 255, num=num_classes)],
        vmin=vv_min,
        vmax=vv_max,
        caption=f'Legend Title - {selected_attribute}'
    )

    fig, ax = plt.subplots()
    img = ax.imshow(raster_data_masked, cmap=cmap, norm=norm)

    image_overlay = folium.raster_layers.ImageOverlay(
        image=img.to_rgba(raster_data_masked, bytes=True),
        bounds=[[geospatial_info["Bounds"][1], geospatial_info["Bounds"][0]],
                [geospatial_info["Bounds"][3], geospatial_info["Bounds"][2]]],
        colormap=lambda x: colormap(x),
    )
    image_overlay.add_to(m)

    colormap.add_to(m)

    plugins.MousePosition().add_to(m)

    end_time = time.time()
    st.sidebar.text(f"Folium Map Created in: {end_time - start_time:.2f} seconds (COG)")

    return m

# Function to display performance indicators for COG
def display_cog_performance_indicators(cog_dataset):
    start_time = time.time()

    # Ajoutez ici vos indicateurs de performance spécifiques au COG
    mosaic_info = MosaicJSON.from_urls([cog_dataset.name])
    num_cog_tiles = len(mosaic_info.tiles) if mosaic_info.tiles else 0  # Nombre de tuiles

    st.sidebar.text(f"Number of COG Tiles: {num_cog_tiles}")

    end_time = time.time()
    st.sidebar.text(f"Performance Indicators Calculated in: {end_time - start_time:.2f} seconds (COG)")

def main():
    st.title("Visualization of GeoTIFF and COG ")

    path_to_geoparquet = "C:\\Users\\medam\\Downloads\\streamlit\\DONNEE_MAROC.parquet"
    gdf = load_data(path_to_geoparquet)

    gdf['Date'] = pd.to_datetime(gdf['Date'])

    selected_attribute = st.sidebar.selectbox("Select attribute", [
        'Indice_Q_',
        'Taux_occ_',
        'Taux_plu_'
    ])

    selected_day = st.sidebar.slider("Select day", 0, 6, 0)

    selected_column_day = f'{selected_attribute}{selected_day}'

    if selected_column_day in gdf.columns:
        if not pd.api.types.is_numeric_dtype(gdf[selected_column_day].dtype):
            pass
        else:
            filtered_data = gdf[gdf[selected_column_day] >= 0]

            x_min, x_max, y_min, y_max = filtered_data.total_bounds
            x_res, y_res = 0.1, 0.1
            x_steps, y_steps = int((x_max - x_min) / x_res), int((y_max - y_min) / y_res)

            x_vals = np.linspace(x_min, x_max, x_steps)
            y_vals = np.linspace(y_min, y_max, y_steps)
    else:
        st.warning(f"Column '{selected_column_day}' not found in the GeoDataFrame.")

    geo_tiff_file_path = f"C:\\Users\\medam\\Downloads\\streamlit\\images\\{selected_attribute}{selected_day}.tif"
    cog_file_path = f"C:\\Users\\medam\\Downloads\\streamlit\\images\\cog{selected_attribute}{selected_day}.tif"
    

    # Added comments to specify each GeoTIFF loaded
    geo_tiff_dataset = read_geotiff(geo_tiff_file_path, "Original")
    cog_dataset = read_geotiff(cog_file_path, "COG")

    geo_tiff_geospatial_info = get_geospatial_info(geo_tiff_dataset)
    cog_geospatial_info = get_geospatial_info(cog_dataset)

    zoom_level_cog = st.sidebar.slider("Select Zoom Level for COG Map", min_value=1, max_value=20, value=5)
    zoom_level_geotiff = st.sidebar.slider("Select Zoom Level for GeoTIFF Map", min_value=1, max_value=20, value=5)

    cog_folium_map = create_folium_map_with_mask_and_mouse_position(
        cog_dataset, cog_geospatial_info, selected_attribute, zoom_level=zoom_level_cog
    )

    geo_tiff_folium_map = create_geotiff_folium_map_with_mask_and_mouse_position(
        geo_tiff_dataset, geo_tiff_geospatial_info, selected_attribute, zoom_level=zoom_level_geotiff
    )

    col1, col2 = st.columns(2)

    with col1:
        st.write("GeoTIFF Basemap with raster layer, mask, and value display:")
        if geo_tiff_dataset:
            st.components.v1.html(geo_tiff_folium_map.get_root().render(), height=600)
            # Display GeoTIFF performance indicators
            st.write("GeoTIFF Performance Indicators:")
            # Add performance indicators specific to GeoTIFF
        else:
            st.warning("GeoTIFF map not available.")

    with col2:
        st.write("COG Basemap with raster layer, mask, and value display:")
        st.components.v1.html(cog_folium_map.get_root().render(), height=600)
        # Display COG performance indicators
        st.write("COG Performance Indicators:")
        display_cog_performance_indicators(cog_dataset)

    st.info("Chargement des données terminé. Vous pouvez maintenant explorer les données.")

# Run the Streamlit app
if __name__ == "__main__":
    main()