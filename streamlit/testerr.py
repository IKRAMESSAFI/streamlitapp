import geopandas as gpd
import folium
from streamlit_folium import folium_static
import plotly.express as px
import pandas as pd
import streamlit as st

def app():

    # Charger la GeoDataFrame depuis le fichier geoparquet
    path = "C:\\Users\\medam\\Downloads\\streamlit\\DONNEE_MAROC.parquet"
    gdf = gpd.read_parquet(path)

    # Titre de la page
    st.title("Graphes interactifs")

    # Sélectionner le point sur la carte pour afficher les données dans la barre latérale
    selected_point_idx = st.sidebar.selectbox("Sélectionnez un point sur la carte pour afficher les données", gdf.index)

    # Ajouter un élément HTML/CSS/JavaScript pour mettre à jour la barre de recherche
    st.markdown(f"""
        <script>
            var selected_point_idx = {selected_point_idx};
            // Fonction pour mettre à jour la barre de recherche avec l'ID du point sélectionné
            function updateSearchBar() {{
                document.getElementById("CustomSearchBox").value = selected_point_idx;
            }}
            // Attacher la fonction au clic sur la carte
            document.addEventListener('DOMContentLoaded', function () {{
                var map = document.getElementById("map");
                map.addEventListener('click', updateSearchBar);
            }});
        </script>
    """, unsafe_allow_html=True)

    # Afficher les données du point sélectionné dans la barre latérale
    if selected_point_idx is not None:
        st.sidebar.write(f"Graphique du point sélectionné (ID: {selected_point_idx}):")
        selected_point_data = gdf.loc[selected_point_idx]

        chart_data = pd.DataFrame({
            'Jours': range(1, 7),
            'Indice_Q_': [selected_point_data[f"Indice_Q_{j}"] for j in range(1, 7)],
            'Taux_occ_': [selected_point_data[f"Taux_occ_{j}"] for j in range(1, 7)],
            'Taux_plu_': [selected_point_data[f"Taux_plu_{j}"] for j in range(1, 7)]
        })

        chart = px.line(chart_data, x='Jours', y=['Indice_Q_', 'Taux_occ_', 'Taux_plu_'],
                        labels={'value': 'Taux', 'variable': 'Type'},
                        title='Variation du qualité de l\'aire, du taux d\'occupation et de pluie',
                        template="plotly")

        # Ajouter le graphique Plotly dans la barre latérale avec une largeur adaptable
        #st.sidebar.plotly_chart(chart, use_container_width=True)

    # Créer une carte interactive avec Folium
    m = folium.Map(location=[31.7917, -7.0926], zoom_start=5, id="map")  # Coordonnées du Maroc

    # Ajouter des marqueurs pour chaque point dans la GeoDataFrame
    for index, row in gdf.iterrows():
        folium.CircleMarker(
            location=[row['geometry'].y, row['geometry'].x],
            radius=5,  # Adjust the radius as needed
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.6,
            popup=f"ID: {index}"
        ).add_to(m)

    # Afficher la carte Folium dans Streamlit
    folium_static(m)

    # Ajouter un commentaire à côté du graphique
    st.write("Variation du taux d'occupation et de pluie")

    # Ajouter un commentaire sur le graphique pour indiquer le comportement de la légende
    st.markdown("**Cliquez sur les éléments de la légende pour activer ou désactiver les attributs**")

    # Ajouter la condition pour afficher le graphique sélectionné
    if selected_point_idx is not None:
        st.plotly_chart(chart, use_container_width=True)
