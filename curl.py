import requests
from requests.auth import HTTPBasicAuth
import rasterio
import numpy as np
from pathlib import Path
from imageio import imwrite   # or from PIL import Image
import os
from PIL import Image
import numpy as np
from pathlib import Path
import io
from google.cloud import storage   # ↳ pip install google-cloud-storage
from typing import Iterable, Union
from multiprocessing import Pool, cpu_count
from multiprocessing.pool import ThreadPool

# -------------------------- GLOBAL CONFIG --------------------------
# (set these before any function definitions so they are available
#  as globals throughout the module)

CHUNK_LENGTH = 500  # pixels per side for chunks
BUCKET       = "processed_tif_images"   # <-- change to your bucket name
GCS_PREFIX   = "glad_chunks"            # object prefix inside bucket

# Geographic bounding boxes: (lon_min, lon_max, lat_max, lat_min)
BOUNDS = [
    (-62,  -50, -8,  -15),   # 62W-50W, 8S-15S
    (-110, -103, 43,  35),   # 110W-103W, 43N-35N
    ( 75,    82, 30,  23),   # 75E-82E,  30N-23N
]

# -------------------------------------------------------------------

def process_image_to_chunks(image_path, chunk_length, crop_pixels=2):
    """
    Process a single 4004x4004 image: crop 2 pixels from each side and split into chunks.
    
    Args:
        image_path: Path to the input image
        chunk_length: Size of each square chunk (must divide 4000 evenly)
        crop_pixels: Number of pixels to crop from each side (default: 2)
    
    Returns:
        List of PIL Image objects (chunks)
    """
    # Load image
    img = Image.open(image_path)
    
    # Get original dimensions
    width, height = img.size
    
    # Crop 2 pixels from each side
    # left, top, right, bottom
    cropped_img = img.crop((crop_pixels, crop_pixels, 
                           width - crop_pixels, height - crop_pixels))
    
    # After cropping: should be 4000x4000
    cropped_width, cropped_height = cropped_img.size
    
    # Calculate number of chunks per dimension
    chunks_per_row = cropped_width // chunk_length
    chunks_per_col = cropped_height // chunk_length
    
    # Extract chunks
    chunks = []
    for row in range(chunks_per_row):
        for col in range(chunks_per_col):
            # Calculate chunk boundaries
            left = col * chunk_length
            top = row * chunk_length
            right = left + chunk_length
            bottom = top + chunk_length
            
            # Extract chunk
            chunk = cropped_img.crop((left, top, right, bottom))
            chunks.append(chunk)
    
    print("Image {} -> {} chunks of {}x{}".format(
        os.path.basename(image_path), len(chunks), chunk_length, chunk_length))
    
    return chunks

def process_dataset_to_chunks(input_dir, output_dir, chunk_length, crop_pixels=2):
    """
    Process an entire dataset of 4004x4004 images into chunks.
    
    Args:
        input_dir: Directory containing input images
        output_dir: Directory to save chunk images
        chunk_length: Size of each square chunk
        crop_pixels: Number of pixels to crop from each side
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Supported image formats
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    total_chunks = 0
    processed_images = 0
    
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        
        # Check if it's an image file
        if os.path.isfile(file_path) and Path(filename).suffix.lower() in supported_formats:
            try:
                # Process the image into chunks
                chunks = process_image_to_chunks(file_path, chunk_length, crop_pixels)
                
                # Save each chunk
                base_name = Path(filename).stem  # filename without extension
                extension = Path(filename).suffix
                
                for i, chunk in enumerate(chunks):
                    chunk_filename = "{}_chunk_{:03d}{}".format(base_name, i, extension)
                    chunk_path = os.path.join(output_dir, chunk_filename)
                    chunk.save(chunk_path)
                
                total_chunks += len(chunks)
                processed_images += 1
                
            except Exception as e:
                print("Error processing {}: {}".format(filename, str(e)))
    
    print("\nProcessed {} images into {} total chunks".format(processed_images, total_chunks))
    print("Chunk size: {}x{} pixels".format(chunk_length, chunk_length))

def calculate_chunk_info(chunk_length):
    """
    Calculate and display information about chunking for 4000x4000 images.
    
    Args:
        chunk_length: Size of each square chunk
    """
    if 4000 % chunk_length != 0:
        print("WARNING: {} does not divide 4000 evenly!".format(chunk_length))
        print("Choose a chunk_length that divides 4000 evenly.")
        print("Good options: 1, 2, 4, 5, 8, 10, 16, 20, 25, 40, 50, 80, 100, 125, 200, 250, 400, 500, 800, 1000, 2000, 4000")
        return False
    
    chunks_per_dimension = 4000 // chunk_length
    total_chunks_per_image = chunks_per_dimension * chunks_per_dimension
    
    print("=== CHUNKING INFO ===")
    print("Original: 4004x4004 -> Cropped: 4000x4000")
    print("Chunk size: {}x{}".format(chunk_length, chunk_length))
    print("Chunks per row/column: {}".format(chunks_per_dimension))
    print("Total chunks per image: {}".format(total_chunks_per_image))
    
    return True

def download_tif(lat, tile, interval, outfolder, outfile):
    username = "glad"
    password = "ardpas"
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

        # Optional: use the local `extract_bands` helper (defined below)
        bands, meta = extract_bands(outfile)
        # e.g. compute NDVI, statistics, etc. as needed
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

def save_rgb(
    tif_path,
    output_path,
    stretch="percentile",   # "linear" or "percentile"
    perc=(2, 98),            # for percentile stretch
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
        if hi == lo:                       # constant image – fall back to linear
            rgb8 = np.clip(rgb / 40000 * 255, 0, 255).astype(np.uint8)
        else:
            rgb8 = np.clip((rgb - lo) / (hi - lo), 0, 1) * 255
            rgb8 = rgb8.astype(np.uint8)

    else:
        raise ValueError("stretch must be 'linear' or 'percentile'")

    # ------------------------------------------------------------------
    # 2.  If the image is effectively empty (all 0 or constant), skip
    # ------------------------------------------------------------------
    if np.all(rgb8 == rgb8.flat[0]):
        # constant image → likely no data / fully cloud-masked
        print(f"⬛  {tif_path.name} appears empty – skipping tile")
        return False

    # Otherwise save the preview image
    imwrite(output_path, rgb8)          # out_path = "rgb.png" or ".jpg"
    print("saved:", output_path)
    return True

def upload_to_gcs_cleanup(
    folder: Union[str, Path],
    bucket_name: str,
    gcs_prefix: str = "",
    delete_after: bool = True,
    supported_ext: Iterable[str] = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"),
):
    """Upload *all* images in a local folder to a GCS bucket then (optionally) delete them.

    Parameters
    ----------
    folder : str | pathlib.Path
        Local directory containing the images you want to push.
    bucket_name : str
        Target GCS bucket (must already exist and be writable by your credentials).
    gcs_prefix : str, optional
        "Folder" (object prefix) inside the bucket. Pass "" for the bucket root.
    delete_after : bool, default True
        If True (default) the local file is removed **only after** a successful upload.
    supported_ext : iterable[str], optional
        File extensions (lower-case, with dot) that will be considered images.
    """

    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"{folder} is not a directory or does not exist")

    # Gather files with supported extensions
    candidates = [p for p in folder.iterdir() if p.suffix.lower() in supported_ext and p.is_file()]
    if not candidates:
        print(f"No image files with extensions {supported_ext} found in {folder}")
        return

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    for local in candidates:
        blob_name = f"{gcs_prefix.rstrip('/')}/{local.name}" if gcs_prefix else local.name
        blob = bucket.blob(blob_name)

        print(f"Uploading {local} → gs://{bucket_name}/{blob_name} …")
        blob.upload_from_filename(local)
        print("✅ upload complete")

        if delete_after:
            try:
                local.unlink()
                print(f"🗑️  removed local copy: {local}")
            except OSError as e:
                print(f"⚠️  could not delete {local}: {e}")

# =============================================================
# PARALLEL ANALYSIS UTILITIES
# =============================================================

def analyze_single_tif(tif_path: Union[str, Path]):
    """Quickly inspect a GeoTIFF and return basic per-band stats.

    Parameters
    ----------
    tif_path : str | pathlib.Path
        Path to the *.tif file.
    """
    tif_path = Path(tif_path)

    if not tif_path.exists():
        return {"file": str(tif_path), "status": "file_not_found"}

    try:
        # ---------------- full per-tile pipeline ----------------
        interval = tif_path.stem  # e.g. "910"
        tile_name = tif_path.parent.name

        png_path = tif_path.with_name(f"{interval}_rgb.png")

        # 1. create RGB quick-look; skip if empty
        if not save_rgb(tif_path, png_path):
            tif_path.unlink(missing_ok=True)
            return {"file": str(tif_path), "status": "empty"}

        # 2. chunk
        chunk_dir = tif_path.parent / f"chunks_{interval}"
        chunk_dir.mkdir(exist_ok=True)
        CHUNK_LENGTH = 500
        chunks = process_image_to_chunks(png_path, CHUNK_LENGTH)
        for i, ch in enumerate(chunks):
            ch.save(chunk_dir / f"{tile_name}_{interval}_chunk_{i:04d}.png")

        # 3. upload
        upload_to_gcs_cleanup(
            folder=chunk_dir,
            bucket_name=BUCKET,
            gcs_prefix=f"{GCS_PREFIX}/{tile_name}/{interval}",
        )

        # 4. clean local files
        for p in [tif_path, png_path]:
            p.unlink(missing_ok=True)

        return {"file": str(tif_path), "status": "uploaded", "chunks": len(chunks)}
    except Exception as e:
        return {"file": str(tif_path), "status": "error", "error": str(e)}

def process_tifs_parallel(tif_paths, max_workers=None, use_threads=True):
    """Run `analyze_single_tif` over many paths concurrently.

    Parameters
    ----------
    tif_paths : list[pathlib.Path]
    max_workers : int | None
        Number of worker threads / processes.
    use_threads : bool, default False
        If True, use a ThreadPool (good for I/O-bound like uploads).
        If False, use a process Pool (good for CPU-bound).
    """

    if max_workers is None:
        # generous default: 4× cores for threads,  cores for processes
        max_workers = (cpu_count() * 4) if use_threads else (cpu_count() or 1)

    PoolClass = ThreadPool if use_threads else Pool

    print(f"Processing {len(tif_paths)} TIFFs with {max_workers} {'threads' if use_threads else 'processes'} …")

    with PoolClass(processes=max_workers) as pool:
        return pool.map(analyze_single_tif, tif_paths)

# ------------------------- MAIN EXECUTION -------------------------
if __name__ == "__main__":
    # 1. constants
    INTERVALS = list(range(392, 394))        # 16-day periods to fetch

    calculate_chunk_info(CHUNK_LENGTH)

    processed_dirs = []        # tile directories touched this run
    download_jobs = []         # (lat_label, tile_name, interval, work_dir, tif_path)

    # 2. iterate tiles inside each bounding window
    bound_index = 0
    for interval in INTERVALS:
        lon_min, lon_max, lat_max, lat_min = BOUNDS[bound_index]
        # full longitude span; we will subsample inside the lat loop
        full_lon_range = range(lon_min, lon_max + 1)
        lat_range = range(lat_max, lat_min - 1, -1)

        for lat_idx, lat in enumerate(lat_range):
            lat_label = f"{abs(lat):02d}{'N' if lat >= 0 else 'S'}"  # e.g. 13N

            # --- staggered lon sampling: take every 3rd degree with row-dependent offset ---
            lon_offset = lat_idx % 3  # 0,1,2 cycling
            lon_iter = [lon for lon in full_lon_range if (lon - lon_min) % 3 == lon_offset]

            for lon in lon_iter:
                lon_label = f"{abs(lon):03d}{'E' if lon >= 0 else 'W'}"  # e.g. 105E
                tile_name = f"{lon_label}_{lat_label}"                 # 105E_13N

                # Folder in ~/Downloads to hold transient files for this tile
                work_dir = Path.home() / "Downloads" / tile_name
                work_dir.mkdir(parents=True, exist_ok=True)
                processed_dirs.append(work_dir)

                tif_path  = work_dir / f"{interval}.tif"

                # queue download job (done later in parallel)
                download_jobs.append(
                    (lat_label, tile_name, interval, work_dir, tif_path)
                )
        bound_index += 1
        bound_index = bound_index % len(BOUNDS)

    # ---------- parallel download phase ----------
    def _dl_job(args):
        lat_label, tile_name, interval, work_dir, tif_path = args
        # ensure directory exists (it might have been removed elsewhere)
        work_dir.mkdir(parents=True, exist_ok=True)
        download_tif(lat_label, tile_name, interval, work_dir, tif_path)
        return tif_path if tif_path.exists() else None

    if download_jobs:
        print(f"Starting {len(download_jobs)} downloads in parallel …")
        with ThreadPool(processes=32) as tp:
            dl_results = tp.map(_dl_job, download_jobs)

    # Build list of TIFFs actually downloaded
    all_tifs = [p for p in dl_results if p]

    # ---------------- PARALLEL PIPELINE ----------------
    if all_tifs:
        results = process_tifs_parallel(all_tifs, max_workers=32, use_threads=True)
        print("results: ", results)
        ok = sum(1 for r in results if r["status"] == "uploaded")
        print(f"\n✅ Parallel pipeline finished: {ok}/{len(results)} tiles uploaded")

    # final cleanup: remove any empty tile directories
    for td in processed_dirs:
        try:
            if td.exists() and not any(td.iterdir()):
                td.rmdir()
        except OSError:
            pass

