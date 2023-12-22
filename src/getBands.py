import rasterio

# Specify the path to the multi-band TIFF file
tif_file_path = r"TIF FILE NAME"

# Open the TIFF file using rasterio
with rasterio.open(tif_file_path) as src:
    # Get the band names or labels
    band_names = src.descriptions

bandNames = {}
for band_idx, band_name in enumerate(band_names, 1):
    bandNames[band_name] = {"band_idx":band_idx,"band_name":band_name}
    #print(f"Band {band_idx}: {band_name}")
print(bandNames)
