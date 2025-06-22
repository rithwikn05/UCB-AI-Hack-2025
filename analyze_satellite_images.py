import os
import glob
import time
import tempfile
from typing import List, Optional
from PIL import Image
from dotenv import load_dotenv
import base64
import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request
import io
from google.cloud import storage
from google.oauth2 import service_account

# Load environment variables
load_dotenv()

def encode_image_to_base64(image_path):
    """Encode image to base64 string"""
    with Image.open(image_path) as img:
        # Convert to RGB if image has an alpha channel
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            
        # Resize if image is too large (optional, adjust as needed)
        max_size = (2048, 2048)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to bytes
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

def analyze_satellite_images(image_paths, output_file="analysis_results.txt"):
    """
    Analyze a list of satellite images using Claude Haiku 3.5
    
    Args:
        image_paths (list): List of paths to satellite images
        output_file (str): Path to save the analysis results
    """
    # Initialize Anthropic client
    print("API Key: ", os.getenv("ANTHROPIC_API_KEY"))
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # System prompt
    system_prompt = "You are an AI assistant tasked with analyzing satellite images to identify and describe geographic and man-made features. Each image covers a square area of around 14 by 14 kilometers. Your goal is to provide a detailed analysis of the image in a structured JSON format.\n\nYou will be presented with a satellite image. Examine the image carefully and identify both geographic and man-made features. For each feature, you should determine its name, location in the image, and approximate size in the image."
    
    # """You are an expert geospatial analyst. Analyze the provided satellite images and provide detailed 
    # information about the following:
    # 1. Geographic features (terrain, water bodies, vegetation, etc.)
    # 2. Man-made structures (buildings, roads, bridges, etc.)
    # 3. Land use patterns (residential, commercial, industrial, agricultural, etc.)
    # 4. Any notable environmental or human activity"""
    
    requests = []
    results = []
    
    for i, image_path in enumerate(image_paths, 1):
        print(f"Processing image {i}/{len(image_paths)}: {os.path.basename(image_path)}")
        
        # Encode image
        base64_image = encode_image_to_base64(image_path)
        
        # Prepare the message with the image
        requests.append(
            Request(
                custom_id=image_path,
                params=MessageCreateParamsNonStreaming(
                    model="claude-3-5-haiku-latest",
                    max_tokens=800,
                    temperature=1,
                    stop_sequences=["json_done"],
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": base64_image,
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": "First, focus on identifying geographic features such as mountains, rivers, lakes, forests, deserts, coastlines, islands, etc. For each feature, determine:\n1. Name: Assign a descriptive name or use a generic term if a specific name is not apparent.\n2. Location: Describe the location within the image (e.g., \"top-left corner\", \"center\", \"bottom-right quadrant\").\n3. Size: Estimate the size relative to the image (e.g., \"covers approximately 20% of the image\", \"spans the entire width of the image\").\n\nNext, identify man-made features such as cities, roads, airports, bridges, dams, agricultural areas, etc. For each feature, determine the same properties as for geographic features:\n1. Name\n2. Location\n3. Size\n\nOrganize your analysis in a JSON format with two main arrays: \"geographic_features\" and \"man_made_features\". Each feature should be an object within its respective array, containing \"name\", \"location\", and \"size\" properties.\n\nHere's an example of how a feature might be described in the JSON format:\n\n{\n  \"geographic_features\": [\n    {\n      \"name\": \"Mountain Range\",\n      \"location\": \"Spans the northern edge of the image\",\n      \"size\": \"Covers approximately 30% of the image area\"\n    }\n  ],\n  \"man_made_features\": [\n    {\n      \"name\": \"Urban Area\",\n      \"location\": \"Southeastern quadrant of the image\",\n      \"size\": \"Occupies about 15% of the image\"\n    }\n  ]\n}\n\nBe as accurate and detailed as possible in your analysis. \n\nNow, analyze the provided satellite image and output your findings in the specified JSON format. End your output with json_done."
                                }
                            ]
                        },
                        {
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "{\n  \"geographic_features\": [\n    {\n      \"name\": \""
                                }
                            ]
                        }
                    ]
                )
            )
        )
    
    print("Requests created: ", len(requests))
    # Send requests to Claude
    responses = client.messages.batches.create(requests=requests)
    
    
    # Save results to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(responses))
    
    print(f"\nAnalysis complete! Results saved to {output_file}")
    return responses

def main():
    # Example usage with GCS
    bucket_name = "processed_tif_images"
    prefix = "glad_chunks/"  # The folder path in your bucket
    output_file = os.path.expanduser("~/Code/UCB-AI-Hack-2025/analysis_results.txt")
  
    
    # Process each image
    ext = ('.jpg', '.jpeg', '.png', '.tif', '.tiff')
    image_paths = []
    print(list(os.walk("~/Code/UCB-AI-Hack-2025/gcsfuse")))
    for root, dirs, files in os.walk("~/Code/UCB-AI-Hack-2025/gcsfuse"):

        for file in files:
            if file.lower().endswith(ext):
                image_paths.append(os.path.join(root, file))
    
    if not image_paths:
        print("No image files found to process.")
        return
    
    print(f"Found {len(image_paths)} images to analyze...\n")
    
    try:
        # Analyze the images
        results = analyze_satellite_images(image_paths, output_file)
        print(f"\nAnalysis complete! Results saved to {output_file}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
    finally:
        # Clean up temporary files
        print("\nCleaning up temporary files...")
        for temp_file in image_paths:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Error removing {temp_file}: {e}")

if __name__ == "__main__":
    main()
