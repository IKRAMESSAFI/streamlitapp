import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from shapely.geometry import Point
def app():
    # Ajout du titre et du sous-titre
    st.title("Filtrage des Données à l'aide des Requêtes: Partie 2")
    st.subheader("Dans cette section, en utilisant des requêtes attributaires, vous pouvez filtrer vos données selon vos besoins et avec des interprétations accompagnées.")

    # Charger le fichier GeoParquet
    fichier_geoparquet = "C:\\Users\\medam\\Downloads\\streamlit\\DONNEE_MAROC.parquet"
    donnees_geo = gpd.read_parquet(fichier_geoparquet)

    # Liste des attributs disponibles
    attributs_disponibles = ['Indice_soc', 'Vitesse']

    # Demander à l'utilisateur de choisir un attribut
    attribut_choisi = st.selectbox("Choisissez un attribut :", attributs_disponibles)

    # Ajouter des interprétations basées sur les valeurs choisies
    if attribut_choisi == "Indice_soc":
        # Afficher l'intervalle possible pour Indice_soc
        st.info("L'Indice socio-économique (Indice_soc) est généralement mesuré dans un intervalle de 0 à 99.")
    elif attribut_choisi == "Vitesse":
        # Afficher l'intervalle possible pour Vitesse
        st.info("La vitesse (Vitesse) est généralement mesurée dans un intervalle de 0 à 49.")
    else:
        st.info("Aucune interprétation disponible pour cet attribut.")

    # Demander à l'utilisateur de saisir une valeur
    seuil_valeur = st.text_input(f"Saisissez une valeur pour {attribut_choisi} :", "50")

    # Vérifier si la valeur saisie est numérique
    try:
        seuil_valeur = float(seuil_valeur)
    except ValueError:
        st.error("Veuillez saisir une valeur numérique.")
        st.stop()

    # Convertir la valeur en un nombre (entier ou réel)
    seuil_valeur = float(seuil_valeur)

    # Ajouter des interprétations basées sur les valeurs choisies
    if attribut_choisi == "Indice_soc":
        if 60.0 <= seuil_valeur <= 99.99:
            st.info("Les zones avec un indice socio-économique élevé peuvent attirer davantage de touristes, ce qui peut augmenter la demande d'hébergement, y compris les hôtels.")
            st.info("Autrement dit, les personnes ayant un pouvoir d'achat plus élevé sont plus susceptibles de voyager et de séjourner dans des hôtels.")
    elif attribut_choisi == "Vitesse":
        if 30 <= seuil_valeur <= 49:
            st.info("Une vitesse de vent plus élevée favorise une dispersion plus efficace des polluants atmosphériques, réduisant ainsi la concentration locale de ces polluants.")
            st.info("Ce qui peut contribuer à améliorer la qualité de l'air dans une région donnée.")
    else:
        st.info("Aucune interprétation disponible pour cet attribut.")

    # Filtrer les données en fonction de l'attribut choisi et de la valeur saisie
    if attribut_choisi == "Indice_soc":
        donnees_filtrees = donnees_geo[donnees_geo['Indice_soc'] > seuil_valeur]
    else:  # attribut_choisi == "Vitesse"
        donnees_filtrees = donnees_geo[donnees_geo['Vitesse_Ve'] > seuil_valeur]

    # Vérifier si des résultats ont été obtenus
    if donnees_filtrees.empty:
        st.warning("Désolé, aucun résultat ne correspond à votre demande.")
    else:
        # Créer une zone tampon autour des points filtrés
        # Increase the buffer distance as needed, for example, 0.5 degrees
        donnees_filtrees['buffer'] = donnees_filtrees['geometry'].buffer(3)

        # Créer une carte Folium centrée sur le Maroc
        carte = folium.Map(location=[31.7917, -7.0926], zoom_start=5)  # Coordonnées approximatives du centre du Maroc

        # Ajouter tous les points à la carte
        for index, row in donnees_geo.iterrows():
            folium.CircleMarker(location=[row.geometry.y, row.geometry.x], radius=2, color='blue', fill=True, fill_color='blue').add_to(carte)

        # Ajouter les points filtrés avec un buffer à la carte
        for index, row in donnees_filtrees.iterrows():
            # Ajouter les points filtrés avec un buffer
            folium.CircleMarker(location=[row.geometry.y, row.geometry.x], radius=20, color='red', fill=True, fill_color='red').add_to(carte)
            
            # Accessing the centroid of the buffer (Polygon)
            buffer_centroid = row['buffer'].centroid
            
            # Adding the buffered area to the map
            folium.Circle(location=[buffer_centroid.y, buffer_centroid.x], radius=2, color='blue', fill=True, fill_color='blue', fill_opacity=0.2).add_to(carte)

        # Afficher la carte avec streamlit
        # Afficher la carte avec streamlit
        folium_static(carte, height=700)

