from fastapi import FastAPI
from pydantic import BaseModel
import base64
from pathlib import Path

app = FastAPI()

class GenerateRequest(BaseModel):
    tile_index: int
    label: str

# Load a tiny placeholder png (64x64 gray square) once.
PLACEHOLDER_PNG_PATH = Path(__file__).with_name("placeholder.png")
if not PLACEHOLDER_PNG_PATH.exists():
    # Create one on the fly if missing.
    from PIL import Image
    img = Image.new("RGB", (64, 64), (128, 128, 128))
    img.save(PLACEHOLDER_PNG_PATH)
with open(PLACEHOLDER_PNG_PATH, "rb") as f:
    PLACEHOLDER_B64 = base64.b64encode(f.read()).decode()

@app.post("/generate")
async def generate(req: GenerateRequest):
    # In real life you'd call your diffusion model here.
    # We just return the placeholder.
    return {
        "tile_index": req.tile_index,
        "image": PLACEHOLDER_B64,
    } 