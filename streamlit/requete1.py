import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
def app():

    # Charger le fichier GeoParquet
    fichier_geoparquet = "C:\\Users\\medam\\Downloads\\streamlit\\DONNEE_MAROC.parquet"
    donnees_geo = gpd.read_parquet(fichier_geoparquet)

    # Titre principal
    st.title("Filtrage des données à l'aide des requêtes : Partie 1")

    # Sous-titre
    st.subheader("Filtrez les données selon vos besoins et obtenez les résultats sur une carte pour une bonne visualisation.")

    # Liste des noms de régions uniques
    noms_regions_uniques = donnees_geo['nomregion'].unique()

    # Demander à l'utilisateur de choisir une région
    nom_region_recherche = st.selectbox("Sélectionnez une région :", noms_regions_uniques)

    # Filtrer les données en fonction du nom de la région
    donnees_filtrees_region = donnees_geo[donnees_geo['nomregion'] == nom_region_recherche]

    # Liste des attributs disponibles
    attributs_disponibles = []
    for i in range(7):  # Ajouter les colonnes de 0 à 6
        attributs_disponibles.extend([f'Taux_plu_{i}', f'Taux_occ_{i}', f'Indice_Q_{i}'])

    # Choix de l'attribut
    attribut_choisi = st.selectbox("Choisissez un attribut :", attributs_disponibles)

    # Filtrer les données en fonction de l'attribut choisi
    if attribut_choisi in donnees_filtrees_region.columns:
        if attribut_choisi.startswith('Taux_plu'):
            # Slider pour Taux_plu (0 à 50)
            seuil_taux_plu = st.slider(f"Sélectionnez le seuil pour {attribut_choisi} :", min_value=0, max_value=50, value=25)
            donnees_filtrees_attribut = donnees_filtrees_region[donnees_filtrees_region[attribut_choisi] > seuil_taux_plu]
        elif attribut_choisi.startswith('Taux_occ'):
            # Sliders pour Taux_occ (0 à 20 pour la valeur minimale et maximale)
            taux_occ_min = st.slider(f"Sélectionnez la valeur minimale pour {attribut_choisi} :", min_value=0, max_value=20, value=10)
            taux_occ_max = st.slider(f"Sélectionnez la valeur maximale pour {attribut_choisi} :", min_value=taux_occ_min, max_value=20, value=20)
            donnees_filtrees_attribut = donnees_filtrees_region[(donnees_filtrees_region[attribut_choisi] >= taux_occ_min) & (donnees_filtrees_region[attribut_choisi] <= taux_occ_max)]
        elif attribut_choisi.startswith('Indice_Q'):
            # Slider pour Indice_Q (0 à 100)
            seuil_indice_q = st.slider(f"Sélectionnez le seuil pour {attribut_choisi} :", min_value=0, max_value=100, value=50)
            donnees_filtrees_attribut = donnees_filtrees_region[donnees_filtrees_region[attribut_choisi] > seuil_indice_q]
        else:
            # Autres attributs sans sliders
            donnees_filtrees_attribut = donnees_filtrees_region.dropna(subset=['geometry', attribut_choisi])

        # Vérifier si la DataFrame n'est pas vide après le filtrage
        if not donnees_filtrees_attribut.empty:
            # Créer la carte Folium
            carte_attribut = folium.Map(location=[donnees_filtrees_attribut.geometry.y.mean(), donnees_filtrees_attribut.geometry.x.mean()], zoom_start=5)

            # Ajouter les points à la carte
            for index, row in donnees_filtrees_attribut.iterrows():
                folium.CircleMarker(location=[row.geometry.y, row.geometry.x], radius=5, color='red', fill=True, fill_color='red').add_to(carte_attribut)

            # Afficher la carte dans Streamlit
            st.subheader(f"Carte des points filtrés pour l'attribut {attribut_choisi}")
            folium_static(carte_attribut,height=700)
        else:
            st.warning("Désolé, aucun résultat ne correspond à votre demande.")
    else:
        st.warning(f"Aucune colonne ne correspond à l'attribut choisi {attribut_choisi}.")