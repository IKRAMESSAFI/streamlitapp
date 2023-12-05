import leafmap

folder = "C:\Users\medam\Downloads\streamlit\images" 

# Boucle pour convertir chaque fichier tiff en COG
for attribute in ['temperature', 'pression_atmosph', 'pluviometrie']:
    for i in range(6):
        in_tiff = f"{folder}/{attribute.lower()}{i}.tif"  # 
        out_cog = f"{folder}/cog{attribute.lower()}{i}.tif"  # Chemin de sortie pour le COG
        
        # Convertir le fichier tiff en COG
        arr = leafmap.image_to_numpy(in_tiff)
        leafmap.numpy_to_cog(arr, out_cog, profile=in_tiff)
