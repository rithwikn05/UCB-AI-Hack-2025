from flask import Flask, render_template, request, jsonify, url_for, redirect
import os
import random
from climate_agent.working_climate_agents import llm_analyze_location
import google.genai as genai
from google.genai import types
from PIL import Image
from io import BytesIO
import json
import asyncio
import shutil
from pydantic import BaseModel

app = Flask(__name__)
GOOGLE_API_KEY='AIzaSyA2_Vvj0cDn0Ldczxc9HsvuwHMLHdmQsd8'
latitude = None
longitude = None
label_path = None
image_path = None

# Placeholder for button labels (could be dynamically set by REST API later)


class ImageFeature(BaseModel):
    name: str
    location: str
    size: str

class ImageDescription(BaseModel):
    geographic_features: list[ImageFeature]
    man_made_features: list[ImageFeature]


def generate_modified_satellite_image(prompt, image_path, output_path='output.png'):

    image = Image.open(image_path)

    client = genai.Client(api_key=GOOGLE_API_KEY)

    text_input = ("The input image is a satellite image with various fearures. Modify the image to match the fearures in the following json:\n\n" + prompt)

    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=[text_input, image],
        config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
        )
    )
    out = ""
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            out += part.text
        elif part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            image.save(output_path)
    return out

def get_disaster_prevention_techniques(prompt):
    client = genai.Client(api_key=GOOGLE_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"Generate 4 specific climate change disaster prevention techniques as a comma-separated list. Input disasters: {prompt}. Return ONLY the comma-separated list, no extra text. Example format: prescribed burn, solar panel installation, direct carbon capture, reforestation",
        config=types.GenerateContentConfig(
            maxOutputTokens=50,
            response_modalities=['TEXT']
        )
    )
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            # Clean up the response - remove any extra text and get just the techniques
            text = part.text.strip()
            # If the response contains a colon, take everything after it
            if ":" in text:
                text = text.split(":")[-1].strip()
            # Remove any leading/trailing quotes or extra formatting
            text = text.replace('"', '').replace("'", "").strip()
            return text
    return "prescribed burn, solar panel installation, direct carbon capture, reforestation"

def generate_image_description(image_path):
    """Generate a JSON description of the satellite image"""
    try:
        image = Image.open(image_path)
        client = genai.Client(api_key=GOOGLE_API_KEY)
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                "Analyze this satellite image and describe the geographic and man-made features you can see. Focus on terrain, vegetation, water bodies, buildings, roads, and other notable features.",
                image
            ],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT'],
                response_mime_type="application/json",
                response_schema=ImageDescription
            )
        )
        return response.parsed.model_dump_json()
    except Exception as e:
        print(f"Error generating image description: {e}")
        # Return a default description
        default_desc = ImageDescription(
            geographic_features=[
                ImageFeature(name="terrain", location="center", size="large"),
                ImageFeature(name="vegetation", location="scattered", size="medium")
            ],
            man_made_features=[
                ImageFeature(name="unknown", location="unknown", size="small")
            ]
        )
        return default_desc.model_dump_json()

def time_evolve_json_description(json_description, climate_prevention_technique, latitude, longitude):
    client = genai.Client(api_key=GOOGLE_API_KEY)
    # Ensure latitude and longitude are strings
    lat_str = str(latitude) if latitude is not None else "0"
    lon_str = str(longitude) if longitude is not None else "0"
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Simulate the effects of climate change and human activities over a period of 5 years on the following satellite image description in JSON format: {json_description}\n\nThe image reflects a 14km by 14km area at latitude {lat_str} and longitude {lon_str}. Assume the following climate prevention technique is being used: {climate_prevention_technique}",
        config=types.GenerateContentConfig(
            system_instruction="You are a climate change simulation engine. You specialize in simulating the effects of climate change and human activities on satellite image descriptions in JSON format. Ensure that every word in the string is seperated by a space.\n\n",
            response_modalities=['TEXT'],
            response_mime_type="application/json",
            response_schema=ImageDescription
        ),
    )
    # print(response)
    return response.parsed.model_dump_json()

@app.route('/')
def index():
    global latitude, longitude, label_path, image_path
    
    # Choose a random index between 1 and 1000
    random_index = random.randint(1, 1000)

    image_path   = None
    sentence_path = None
    analysis     = None
    buttons      = []          # ← ensure the name exists even on error
    image_url    = None        # Initialize image_url

    try:
        with open("img_paths.txt", "r") as img_file:
            img_paths = img_file.readlines()
            if random_index <= len(img_paths):
                image_path = img_paths[random_index - 1].strip()

        print(image_path)

        with open("labels_paths.txt", "r") as label_file:
            label_paths = label_file.readlines()
            if random_index <= len(label_paths):
                label_path = label_paths[random_index - 1].strip()

                # Extract lat/lon from the label path
                if "W" in label_path:
                    lon_part = label_path.split("_")[1]
                    longitude = -int(''.join(filter(str.isdigit, lon_part)))
                elif "E" in label_path:
                    lon_part = label_path.split("_")[1]
                    longitude = int(''.join(filter(str.isdigit, lon_part)))
                else:
                    longitude = 0

                if "S" in label_path:
                    lat_part = label_path.split("_")[2]
                    latitude = -int(''.join(filter(str.isdigit, lat_part)))
                elif "N" in label_path:
                    lat_part = label_path.split("_")[2]
                    latitude = int(''.join(filter(str.isdigit, lat_part)))
                else:
                    latitude = 0

                print(f"Latitude: {latitude}, Longitude: {longitude}")
                
                # Store in global variables
                globals()['latitude'] = latitude
                globals()['longitude'] = longitude
                globals()['label_path'] = label_path
                
                # llm_analyze_location is async; run it synchronously here
                raw = asyncio.run(llm_analyze_location(latitude, longitude, "urgent"))

                # if it's already a string, keep it; if it's a dict, grab the first value
                if isinstance(raw, dict):
                    # adjust the key to whatever llm_analyze_location actually returns
                    analysis_text = raw.get("disasters", "") or raw.get("text", "")
                else:
                    analysis_text = str(raw)

                # guard against empty result
                if not analysis_text:
                    analysis_text = "wildfire, flood, drought, storm"   # default

                print("analysis =", analysis_text)

                # pass the plain string to Gemini
                techniques = get_disaster_prevention_techniques(analysis_text)
                print(f"Raw techniques response: {techniques}")
                
                # Split and clean the techniques
                buttons = [s.strip() for s in techniques.split(',') if s.strip()]
                
                # Filter out any buttons that look like prompts or instructions
                buttons = [btn for btn in buttons if not any(word in btn.lower() for word in ['here are', 'disaster', 'listed', 'technique', 'prevention', 'input', 'output'])]
                
                print(f"Cleaned buttons: {buttons}")

                # If we don't have enough good buttons, use defaults
                if len(buttons) < 4:
                    default_techniques = ["reforestation", "solar panel installation", "water conservation", "sustainable agriculture"]
                    buttons.extend(default_techniques[len(buttons):])

                buttons = buttons[:4]                               # trim to exactly 4

                if os.path.exists(label_path):
                    with open(label_path, "r") as sent_file:
                        sentence_path = sent_file.read().strip()

        # Process image path for Flask static serving
        if image_path and image_path.startswith("/static/"):
            # Remove the leading /static/ to get the relative path within static folder
            rel_inside_static = image_path[len("/static/"):]
            abs_file = os.path.join(app.root_path, "static", rel_inside_static)
            if os.path.isfile(abs_file):
                image_url = url_for("static", filename=rel_inside_static)
                # Store the absolute file path in global variable
                globals()['image_path'] = abs_file
            else:
                print(f"Image file not found: {abs_file}")
                image_url = None

    except Exception as e:
        print(f"Error reading paths: {e}")

    # Check if we have a generated image to show instead
    generated_image_path = os.path.join(app.root_path, "static", "gemini_output.png")
    if os.path.exists(generated_image_path):
        image_url = url_for("static", filename="gemini_output.png")
        print("Showing generated image: gemini_output.png")

    return render_template(
        'index.html',
        button_labels=buttons,  # Changed to match template
        image_url=image_url
    )

@app.route('/disaster', methods=['POST'])
def disaster():
    data = request.get_json()
    disaster_type = data.get('disaster')

    # Simply return the disaster type for now; no image generation
    return jsonify({"status": "received", "disaster": disaster_type})

@app.route('/trigger/<disaster_name>')
def trigger_disaster(disaster_name):
    global latitude, longitude, label_path, image_path
    
    try:
        button_label = disaster_name

        # Check if we have the required global variables
        if not all([latitude, longitude, label_path, image_path]):
            return jsonify({
                "status": "error", 
                "message": "Missing required data. Please refresh the page.",
                "disaster": disaster_name
            })

        print(f"Triggering disaster simulation for: {button_label}")
        print(f"Using coordinates: {latitude}, {longitude}")
        print(f"Label path: {label_path}")
        print(f"Image path: {image_path}")

        # Read the current image description from label file
        if os.path.exists(label_path):
            with open(label_path, "r") as f:
                current_description = f.read().strip()
        else:
            # Generate description from image if label file doesn't exist
            current_description = generate_image_description(image_path)

        print("Generating time evolution...")
        new_json = time_evolve_json_description(
            json_description=current_description,
            climate_prevention_technique=button_label,
            latitude=str(latitude),
            longitude=str(longitude)
        )

        print("Generating modified satellite image...")
        output_path = os.path.join(app.root_path, "static", "gemini_output.png")
        simulation_description = generate_modified_satellite_image(
            prompt=new_json,
            image_path=image_path,
            output_path=output_path
        )

        # Update the global image_path to point to the new generated image
        globals()['image_path'] = output_path
        
        print(f"Generated image saved to: {output_path}")
        
        # Redirect back to index page to show the new image
        return redirect('/')
        
    except Exception as e:
        print(f"Error in trigger_disaster: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "disaster": disaster_name
        })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
