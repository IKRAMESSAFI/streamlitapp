import streamlit as st
def app():
    import geopandas as gpd
    import folium
    from streamlit_folium import folium_static
    import matplotlib.pyplot as plt
    from io import BytesIO
    import base64
    import time
    # Charger la GeoDataFrame depuis le fichier geoparquet
    path = "C:\\Users\\medam\\Downloads\\streamlit\\DONNEE_MAROC.parquet"
    gdf = gpd.read_parquet(path)
    with st.spinner("Chargement des données en cours ... veuillez patienter un peu..."):
        # Mettre en pause pendant 2 secondes pour simuler un chargement long
        time.sleep(80)

    # Titre de la page
    st.title("Pop-ups intégrant des graphes")

    # Afficher la carte interactive avec Folium en plein écran avec un zoom initial plus élevé
    m = folium.Map(location=[gdf.geometry.y.mean(), gdf.geometry.x.mean()], zoom_start=5, fullscreen=True)

    # Définir une variable pour stocker l'index du point sélectionné
    selected_point_idx = None

    def on_click(e):
        global selected_point_idx
        # Récupérer l'index du point cliqué
        selected_point_idx = e.target.options['custom_id']

    # Fonction pour générer le graphique et le popup
    def generate_popup(row, y_attributes):
        # Créer un seul graphique avec Matplotlib pour les trois attributs
        fig, ax = plt.subplots(figsize=(3, 2))

        for attribute in y_attributes:
            # Sélectionner les colonnes de variation associées à l'attribut
            variation_values = [row[f"{attribute}_{j}"] for j in range(0, 6)]

            # Tracer la courbe
            ax.plot(range(1, 7), variation_values, label=f'{attribute}')

        ax.set_title("Variation des attributs spatio-temporels")
        ax.set_xlabel("Jours")
        ax.set_ylabel("Variation")
        ax.legend()

        # Convertir le graphique en image
        image_stream = BytesIO()
        plt.savefig(image_stream, format='png')
        image_stream.seek(0)

        # Convertir l'image en base64
        image_base64 = base64.b64encode(image_stream.read()).decode()

        # Ajouter le contenu HTML de l'image comme popup sur la carte Leaflet
        popup = folium.Popup(f"<img src='data:image/png;base64,{image_base64}'/>", max_width=200)
        return popup, fig

    # Ajouter des cercles colorés à la carte avec des identifiants personnalisés
    for idx, row in gdf.iterrows():
        color = 'blue'  # Couleur du cercle
        popup_content = f"<strong>Point ID:</strong> {idx}<br>" \
                        f"<strong>Nom de la région:</strong> {row['nomregion']}<br>" \
                        f"<strong>Indice socio-économique:</strong> {row['Indice_soc']}<br>" \
                        f"<strong>Vitesse du Vent:</strong> {row['Vitesse_Ve']}<br>"

        popup, _ = generate_popup(row, ['Indice_Q', 'Taux_occ', 'Taux_plu'])

        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=5,  # Ajuster la taille du cercle
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=popup,
            tooltip=f"Point ID: {idx}",
            custom_id=idx  # Ajouter un attribut personnalisé pour stocker l'index
        ).add_to(m)

    # Afficher la carte dans le Dashboard avec une hauteur plus grande
    folium_static(m, height=800)

    # Afficher le graphique en tant que popup une fois le point cliqué
    if selected_point_idx is not None:
        st.write(f"Graphique du point sélectionné (ID: {selected_point_idx}):")
        selected_point_data = gdf.loc[selected_point_idx]

        popup, fig = generate_popup(selected_point_data, ['Indice_Q', 'Taux_occ', 'Taux_plu'])

        # Ajouter le popup à la carte
        folium.Marker(
            location=[selected_point_data.geometry.y, selected_point_data.geometry.x],
            popup=popup,
            tooltip=f"Point ID: {selected_point_idx}",
            custom_id=selected_point_idx
        ).add_to(m)

        # Afficher le graphique dans Streamlit
        st.pyplot(fig)
        # Le message ci-dessous sera affiché après le chargement des données
    st.info("Chargement des données terminé. Vous pouvez maintenant explorer les données .")