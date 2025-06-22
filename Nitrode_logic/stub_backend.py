from fastapi import FastAPI
from pydantic import BaseModel
import base64
import os
from pathlib import Path
import replicate
import requests

app = FastAPI()

class GenerateRequest(BaseModel):
    tile_index: int
    label: str

# ------------------------------------------------------------------
# Utility: run Stable Diffusion via Replicate and return PNG bytes
# ------------------------------------------------------------------
MODEL_ID = "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4"

async def generate_sd_image(prompt: str) -> bytes:
    """Call Replicate to create an image and return raw PNG bytes."""
    full_prompt = f"an aerial view of a landscape that has been affected by {prompt}. Make it zoom out and realistic."

    # Blocking call, but fine for a stub API; could move to threadpool if needed.
    output = replicate.run(MODEL_ID, input={"prompt": full_prompt, "scheduler": "K_EULER"})

    # 'output' is an iterator of file-like objects (or URLs). Grab first.
    first_item = next(iter(output))

    if hasattr(first_item, "read"):
        img_bytes = first_item.read()
    else:
        # item is URL string: download
        img_bytes = requests.get(first_item).content
    return img_bytes

@app.post("/generate")
async def generate(req: GenerateRequest):
    """Generate an image conditioned on the provided label and return base64 PNG."""
    try:
        img_bytes = await generate_sd_image(req.label)
        img_b64 = base64.b64encode(img_bytes).decode()
    except Exception as e:
        # On failure, return an error message instead of crashing server
        return {"error": str(e)}

    return {
        "tile_index": req.tile_index,
        "image": img_b64,
    } 