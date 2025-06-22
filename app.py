from flask import Flask, render_template, request, jsonify, url_for
import os
import random
from climate_agent.working_climate_agents import llm_analyze_location
import google.genai as genai
from google.genai import types
from PIL import Image
from io import BytesIO
import json

app = Flask(__name__)
GOOGLE_API_KEY='AIzaSyA2_Vvj0cDn0Ldczxc9HsvuwHMLHdmQsd8'

# Placeholder for button labels (could be dynamically set by REST API later)

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

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            image.show()
            image.save(output_path)

def get_disaster_prevention_techniques(prompt):
    client = genai.Client(api_key=GOOGLE_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="For each of the following disasters list, generate a single climate change disaster prevention technique and return them as a comma separated list (eg: For input (wildfire, mining operations, industrialization, deforestation) a possible output would be: prescribed burn, solar panel installation, direct carbon capture, reforestation: " + prompt + "\n\n" + "",
        config=types.GenerateContentConfig(
            maxOutputTokens=len(prompt.split(","))*4,
            response_modalities=['TEXT']
        )
    )
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            return part.text
    return "prescribed burn, solar panel installation, direct carbon capture, reforestation"

@app.route('/')
def index():
    # Choose a random index between 1 and 1000
    random_index = random.randint(1, 1000)

    image_path   = None
    sentence_path = None
    analysis     = None
    buttons      = []          # ← ensure the name exists even on error

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

                #print(f"Latitude: {latitude}, Longitude: {longitude}")
                analysis = llm_analyze_location(latitude, longitude, "urgent")
                analysis = get_disaster_prevention_techniques(analysis)
                buttons = [part.strip() for part in analysis.split(',')]

                if os.path.exists(label_path):
                    with open(label_path, "r") as sent_file:
                        sentence_path = sent_file.read().strip()

    except Exception as e:
        print(f"Error reading paths: {e}")

    return render_template(
        'index.html',
        buttons=buttons
    )

@app.route('/disaster', methods=['POST'])
def disaster():
    data = request.get_json()
    disaster_type = data.get('disaster')

    # Simply return the disaster type for now; no image generation
    return jsonify({"status": "received", "disaster": disaster_type})

if __name__ == '__main__':
    app.run(debug=True)
