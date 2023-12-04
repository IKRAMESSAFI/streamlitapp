import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static
def app():
    # Charger les données depuis le fichier GeoParquet
    gdf = gpd.read_parquet("C:\\Users\\medam\\Downloads\\streamlit\\DONNEE_MAROC.parquet")

    # Ajouter un titre
    st.title("Filtrage des Données à l'aide des Requêtes: Partie 3")

    # Ajouter une explication
    st.write("Dans cette section, en utilisant des requêtes attributaires, vous pouvez filtrer vos données selon vos besoins.")

    # Afficher la barre latérale avec les noms des colonnes
    st.sidebar.write("Colonnes disponibles :")
    for column in gdf.columns:
        st.sidebar.write(f"- {column}")

    # Afficher la boîte de texte pour les requêtes attributaires
    query = st.text_input("Entrez votre requête attributaire (ex: nomregion=='SOUSS-MASSA-DRAA' and Indice_soc>=14.8 and Indice_soc<=14.9 )", "")

    # Filtrer les données en fonction de la requête attributaire
    if query:
        # Arrondir les valeurs avant la comparaison
        filtered_gdf = gdf.query(query)
    else:
        filtered_gdf = gdf

    # Filtrer les données en fonction de la requête attributaire
    if query:
        # Convertir la chaîne de date en objet de date
        gdf['Date'] = pd.to_datetime(gdf['Date'])
        # Filtrer les données en fonction de la requête attributaire
        filtered_gdf = gdf.query(query)
    else:
        filtered_gdf = gdf

    # Créer une carte Folium
    m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=5)

    # Ajouter tous les points en bleu
    for index, row in gdf.iterrows():
        folium.CircleMarker(
            location=[row.geometry.centroid.y, row.geometry.centroid.x],
            radius=5,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.7,
            popup=f"{row['nomregion']} - Indice_Q_0: {row['Indice_Q_0']}"
        ).add_to(m)

    # Ajouter les points filtrés en rouge
    if not filtered_gdf.empty:
        for index, row in filtered_gdf.iterrows():
            folium.CircleMarker(
                location=[row.geometry.centroid.y, row.geometry.centroid.x],
                radius=5,
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.7,
                popup=f"{row['nomregion']} - Indice_Q_0: {row['Indice_Q_0']}"
            ).add_to(m)

    # Afficher la carte Folium dans Streamlit
    folium_static(m)