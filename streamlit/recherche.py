import streamlit as st
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from shapely.geometry import Point

def app():
    @st.cache_data(persist=True)
    def load_data(file_path):
        return gpd.read_parquet(file_path)

    # Load the GeoParquet file
    file_path = "C:\\Users\\medam\\Downloads\\streamlit\\DONNEE_MAROC.parquet"
    gdf = load_data(file_path)

    # Sidebar for coordinate search
    search_coordinates = st.sidebar.text_input("Search by Coordinates (lat, lon)", "31.7917, -7.0926")

    # Add a search button
    search_button = st.sidebar.button("Search")
    search_button_color = "#41ae76"

    # Ajouter un commentaire dans la barre latérale
    st.sidebar.markdown("**Note:** Click on the red marker on the map for more information about the highlighted point.")

    # Utilisez la première colonne du GeoDataFrame pour la taille des symboles
    selected_column = gdf.columns[0]
    gdf[selected_column] = pd.to_numeric(gdf[gdf.columns[0]], errors='coerce')

    # Initialize variables for coordinates and information
    lat, lon = 31.7917, -7.0926  # Default coordinates
    highlighted_info = None

    # Check if the search button is clicked
    if search_button:
        # Parse coordinates
        try:
            lat, lon = map(float, search_coordinates.split(','))
        except ValueError:
            st.warning("Invalid coordinates format. Please use 'lat, lon'")
            st.stop()

        # Create a Point geometry for the highlighted coordinates
        highlighted_point = Point(lon, lat)

        # Create a DataFrame for the highlighted point
        highlighted_info = gdf.iloc[gdf.geometry.apply(lambda x: x.distance(highlighted_point)).idxmin()]

    # Base map
    
    fig_map = px.scatter_mapbox(gdf, lat=gdf.geometry.y, lon=gdf.geometry.x,
                                color=gdf[selected_column].fillna(0),
                                size_max=15,
                                zoom=4, center={"lat": lat, "lon": lon})

    # Set a single color for the color scale
    fig_map.update_traces(marker=dict(color='blue'))

    # Add an additional layer for the highlighted point
    fig_map.add_trace(go.Scattermapbox(
        lat=[lat],
        lon=[lon],
        mode='markers',
        marker=dict(size=10, color='red'),
        text='Highlighted Point',
        hoverinfo='text',
    ))

    fig_map.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, b=0, t=0))

    # Highlighted point with popup
    
    fig_popup = go.Figure()

    # Add the base map
    fig_popup.add_trace(fig_map.data[0])

    # Add the highlighted point with an arrow
    fig_popup.add_trace(go.Scattermapbox(
        lat=[lat],
        lon=[lon],
        mode='markers',
        marker=dict(size=10, color='red'),
        text='Highlighted Point',
        hoverinfo='text',
    ))

    # Add a popup with all information
    if highlighted_info is not None:
        popup_text = "<br>".join([f"<b>{col}:</b> {highlighted_info[col]}" for col in highlighted_info.index])
        fig_popup.add_trace(go.Scattermapbox(
            lat=[lat],
            lon=[lon],
            mode='markers',
            marker=dict(size=0),  # Set size to 0 to hide the marker
            text=popup_text,
            hoverinfo='text',
        ))

    # Add a title in the center
    title_html = """
        <h1 style="text-align:center; color: black;">RECHERCHE PAR LATITUDE LONGITUDE</h1>
    """
    st.components.v1.html(title_html, height=100)

    # Adjust the height and width of the layout
    fig_popup.update_layout(
        mapbox_style="carto-positron",
        margin=dict(l=0, r=0, b=0, t=0),
        height=800,  # Adjust the height as needed
        width=1200,   # Adjust the width as needed
        mapbox=dict(zoom=4, center={"lat": lat, "lon": lon}, uirevision='no-zoom-control')  # Set initial zoom level, hide zoom control, and center the map
    )

    # Display maps
    st.plotly_chart(fig_popup)

# Run the app
app()
