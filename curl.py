import requests
from requests.auth import HTTPBasicAuth
import rasterio
import numpy as np
from pathlib import Path
from imageio import imwrite   # or from PIL import Image

def download_tif(lat, tile, interval):
    username = "glad"
    password = "ardpas"

    lat = "13N"  # example
    tile = "105E_13N"
    interval = "920"
    outfolder = "/Users/anikait/Downloads"
    outfile = f"{outfolder}/{interval}.tif"

    url = f"https://glad.umd.edu/dataset/glad_ard2/{lat}/{tile}/{interval}.tif"

    response = requests.get(url, auth=HTTPBasicAuth(username, password), stream=True)

    if response.status_code == 200:
        with open(outfile, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {outfile}")

        # -------- NEW: extract spectral data ----------
        from extract_spectral import extract_bands      # a helper file you create
        bands, meta = extract_bands(outfile)
        # do something with `bands`, e.g., compute NDVI, save statistics, etc.
        # ----------------------------------------------
    else:
        print(f"Failed with status code {response.status_code}: {response.text}")

def extract_bands(tif_path):
    """
    Returns:
        data  : np.ndarray of shape (n_bands, height, width)
        meta  : metadata dict (projection, transform, dtype, etc.)
    """
    with rasterio.open(tif_path) as src:
        # Number of spectral bands in the file
        n_bands = src.count
        print(f"{tif_path.name}: {n_bands} band(s) "
              f"{src.width}×{src.height}, dtype={src.dtypes[0]}")

        # Read all bands into one 3-D array
        data = src.read()            # shape (band, row, col)
        meta = src.meta.copy()

    return data, meta

def save_rgb(tif_path, output_path,stretch="percentile",   # "linear" or "percentile"
    perc=(2, 98)            # for percentile stretch
):
    with rasterio.open(tif_path) as src:
        blue  = src.read(1).astype("float32")
        green = src.read(2).astype("float32")
        red   = src.read(3).astype("float32")

    # stack in R-G-B order
    rgb = np.stack([red, green, blue], axis=-1)

    # ------------------------------------------------------------------
    # 1.  Stretch / rescale 16-bit reflectance (0-40000) → 0-255 uint8
    # ------------------------------------------------------------------
    if stretch == "linear":          # simple 0-40000 → 0-255
        rgb8 = np.clip(rgb / 40000 * 255, 0, 255).astype(np.uint8)

    elif stretch == "percentile":    # clip extremes, then rescale
        lo, hi = np.percentile(rgb, perc)
        rgb8 = np.clip((rgb - lo) / (hi - lo), 0, 1) * 255
        rgb8 = rgb8.astype(np.uint8)

    else:
        raise ValueError("stretch must be 'linear' or 'percentile'")

    # ------------------------------------------------------------------
    # 2.  Write to file
    # ------------------------------------------------------------------
    imwrite(output_path, rgb8)          # out_path = "rgb.png" or ".jpg"
    print("saved:", output_path)

if __name__ == "__main__":
    tif_path = Path("/Users/rithwiknukala/Downloads/920.tif")
    save_rgb(tif_path, "/Users/rithwiknukala/Downloads/920_rgb.png")
    print("saved image")