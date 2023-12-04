import leafmap.foliumap as leafmap
from streamlit_folium import folium_static as st_folium_static
import numpy as np
from branca.colormap import LinearColormap
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import streamlit as st


# Function to generate the URL based on user selections
def generate_url(selected_attribute, selected_day):
    return f"https://ikramessafi.github.io/PROJETIMAGES/{selected_attribute}{selected_day}.tif"

def main():
    

    st.title("SplitMap pour comparer deux cartes  ")
    

    # Sidebar for attribute selection and day slider for each URL
    with st.sidebar.expander("Configurer les options pour URL1"):
        selected_attribute_url1 = st.selectbox("Select attribute", ['Indice_Q_', 'Taux_occ_', 'Taux_plu_'], key="attribute_url1")
        selected_day_url1 = st.slider("Select day", 0, 6, 0, key="day_url1")

    with st.sidebar.expander("Configurer les options pour URL2"):
        selected_attribute_url2 = st.selectbox("Select attribute", ['Indice_Q_', 'Taux_occ_', 'Taux_plu_'], key="attribute_url2")
        selected_day_url2 = st.slider("Select day", 0, 6, 0, key="day_url2")

    # Generate URLs based on user selections
    url1 = generate_url(selected_attribute_url1, selected_day_url1)
    url2 = generate_url(selected_attribute_url2, selected_day_url2)

    # Create a leafmap Map
    m = leafmap.Map()

    # Use split_map to display the images side by side
    m.split_map(url1, url2)

    # Define vmin, vmax, and class_limits based on the selected attribute for URL1
    if selected_attribute_url1 == 'Indice_Q_':
        vmin = 0
        vmax = 100
    elif selected_attribute_url1 == "Taux_occ_":
        vmin = 0
        vmax = 20
    else:
        vmin = 0
        vmax = 50

    class_limits1 = np.linspace(vmin, vmax, num=6)

    # Create a colormap with 6 equal intervals
    colormap = LinearColormap(
        colors=[cm.cividis(x) for x in np.linspace(0, 1, num=6)],
        index=np.linspace(vmin, vmax, num=6),
        vmin=vmin,
        vmax=vmax
    )
    m.add_child(colormap)

    # Render the map using st_folium_static
    st_folium_static(m, width=1200, height=700)

if __name__ == "__main__":
    main()
