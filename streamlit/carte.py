# app_streamlit.py
import streamlit as st
import geopandas as gpd
import plotly.express as px
import pandas as pd
import time
def load_data(file_path):
    """Load GeoParquet file."""
    return gpd.read_parquet(file_path)

def display_loading_message():
    """Display a loading message while data is being loaded."""
    with st.spinner("Chargement des données en cours ... veuillez patienter un peu..."):
        # Simulate a loading delay
        time.sleep(2)

def convert_to_numeric(gdf, selected_column):
    """Convert the selected column to numeric."""
    try:
        gdf[selected_column] = pd.to_numeric(gdf[selected_column])
    except pd.errors.OverflowError as e:
        st.error(f"Error converting {selected_column} to numeric: {e}")
        st.stop()

def create_map(gdf, selected_column):
    st.title("Cartographie Thématique")
    st.write(f"Carte thématique de l'attribut {selected_column}")
    fig_symbols = px.scatter_mapbox(gdf, lat=gdf.geometry.y, lon=gdf.geometry.x,
                                    size=selected_column, color=selected_column,
                                    color_continuous_scale='Viridis', size_max=15,
                                    zoom=4, center={"lat": 31.7917, "lon": -7.0926})
    fig_symbols.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, b=0, t=0))
    st.plotly_chart(fig_symbols)

def main():
    # Load the GeoParquet file
    file_path = "C:\\Users\\medam\\Downloads\\streamlit\\DONNEE_MAROC.parquet"
    gdf = load_data(file_path)
    
    # Display loading message
    display_loading_message()

    # Rest of the code for Streamlit
    columns = [col for col in gdf.columns if col not in ['geometry', 'nomregion', 'Date']]
    selected_column = st.sidebar.selectbox("Choose the column to map", columns)

    # Convert selected column to numeric
    convert_to_numeric(gdf, selected_column)

    # Display the map
    create_map(gdf, selected_column)

    st.info("Chargement des données terminé. Vous pouvez maintenant explorer les données .")

if __name__ == "__main__":
    main()
