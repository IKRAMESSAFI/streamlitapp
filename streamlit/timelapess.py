import streamlit as st
def app():
    import os
    from PIL import Image
    import geopandas as gpd
    import base64
    import imageio
    import folium
    import numpy as np

    import matplotlib.cm as cm  # Ajout de cette ligne
    from branca.colormap import LinearColormap
    from streamlit_folium import folium_static, st_folium



    # Fonction pour convertir une image en base64
    def image_to_base64(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    # Charger les données depuis le fichier GeoParquet
    file_path = "C:\\Users\\medam\\Downloads\\streamlit\\DONNEE_MAROC.parquet"
    try:
        gdf = gpd.read_parquet(file_path)
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        st.stop()

    # Dictionnaire des fichiers GeoTIFF correspondant à chaque attribut
    raster_paths = {
        'Indice_Q': {
            '0': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Indice_Q_0.tif',
            '1': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Indice_Q_1.tif',
            '2': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Indice_Q_2.tif',
            '3': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Indice_Q_3.tif',
            '4': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Indice_Q_4.tif',
            '5': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Indice_Q_5.tif',
            '6': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Indice_Q_6.tif',
        },
        'Taux_occ_': {
            '0': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Taux_occ_0.tif',
            '1': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Taux_occ_1.tif',
            '2': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Taux_occ_2.tif',
            '3': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Taux_occ_3.tif',
            '4': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Taux_occ_4.tif',
            '5': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Taux_occ_5.tif',
            '6': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Taux_occ_6.tif',
        },
        'Taux_plu_': {
            '0': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Taux_plu_0.tif',
            '1': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Taux_plu_1.tif',
            '2': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Taux_plu_2.tif',
            '3': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Taux_plu_3.tif',
            '4': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Taux_plu_4.tif',
            '5': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Taux_plu_5.tif',
            '6': 'C:\\Users\\medam\\Downloads\\streamlit\\RASTERSS\\Taux_plu_6.tif',
        },
    }

    # Sidebar pour la sélection de l'attribut
    selected_attribute = st.sidebar.selectbox("Sélectionnez l'attribut à visualiser", ['Indice_Q', 'Taux_occ_','Taux_plu_'])

    # Créer un graphique temporel avec Altair
    st.title(f" Timelapses permettant  de naviguer entre les différents jours de l'attribut {selected_attribute}")

    # Utiliser leafmap pour créer le timelapse
    output_dir = '/content/timelapse_output'
    os.makedirs(output_dir, exist_ok=True)  # Créer le répertoire s'il n'existe pas
    output_gif_path = os.path.join(output_dir, f'output_timelapse_{selected_attribute}.gif')

    try:
        images = list(raster_paths[selected_attribute].values())
        #st.write(f"Liste des images pour le timelapse : {images}")

        # Create a list to store PIL Image objects
        pil_images = []

        for image_path in images:
            img = Image.open(image_path)

            # Resize the image to the desired size
            new_size = (800, 960)
            resized_img = img.resize(new_size, resample=Image.LANCZOS)

            pil_images.append(resized_img)

        # Save each resized frame as a static image
        for i, pil_image in enumerate(pil_images):
            frame_path = os.path.join(output_dir, f"frame_{i}.png")
            pil_image.save(frame_path)

        # Create GIF from resized static images
        gif_path = os.path.join(output_dir, f'output_timelapse_{selected_attribute}.gif')
        with imageio.get_writer(gif_path, mode='I', duration=1000, loop=0) as writer:
            for frame_path in [f"frame_{i}.png" for i in range(len(pil_images))]:
                img = imageio.imread(os.path.join(output_dir, frame_path))
                resized_img = Image.fromarray(img).resize((800, 960), resample=Image.LANCZOS)  # Ajustez la taille comme souhaité
                writer.append_data(resized_img)

    except Exception as e:
        st.error(f"Erreur lors de la création du timelapse : {e}")
        st.stop()

    # Obtenir les limites (bounds) à partir des données GeoParquet
    bounds = [
        [gdf.bounds.miny.min(), gdf.bounds.minx.min()],
        [gdf.bounds.maxy.max(), gdf.bounds.maxx.max()]
    ]

    # Créer la carte Folium
    m = folium.Map(location=[31.5, -7], zoom_start=5, width=800, height=960)

    # Ajouter le calque GIF à la carte
    gif_layer = folium.raster_layers.ImageOverlay(
        gif_path,
        bounds=bounds,
        opacity=0.7,
        name='GIF Layer'
    ).add_to(m)

    # Ajouter le contrôle de calque à la carte
    folium.LayerControl().add_to(m)

    # Define vmin, vmax, and class_limits based on the selected attribute for URL1
    if selected_attribute == 'Indice_Q':
        vmin = 0
        vmax = 100
    elif selected_attribute == "Taux_occ_":
        vmin = 0
        vmax = 20
    else:
        vmin = 0
        vmax = 50

    class_limits = np.linspace(vmin, vmax, num=6)

    # Create a colormap with 6 equal intervals
    colormap = LinearColormap(
        colors=[cm.cividis(x) for x in np.linspace(0, 1, num=6)],
        index=np.linspace(vmin, vmax, num=6),
        vmin=vmin,
        vmax=vmax
    )
    m.add_child(colormap)

    # Afficher la carte
    folium_static(m, width=1200, height=700)




