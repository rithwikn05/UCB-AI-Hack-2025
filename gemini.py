import os
from google import genai
from google.genai import types
import pydantic
from PIL import Image
from io import BytesIO
import json
from pydantic import BaseModel


class ImageFeature(BaseModel):
    name: str
    location: str
    size: str

class ImageDescription(BaseModel):
    geographic_features: list[ImageFeature]
    man_made_features: list[ImageFeature]


def generate_modified_satellite_image(prompt, image_path, output_path='output.png'):

    image = Image.open(image_path)

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

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
            image.show()
            image.save(output_path)
    return out

def get_disaster_prevention_techniques(prompt):
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
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

def time_evolve_json_description(json_description, climate_prevention_technique, latitude, longitude):
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Simulate the effects of climate change and human activities over a period of 5 years on the following satellite image description in JSON format: " + json_description + "\n\n" + " The image reflects a 14km by 14km area at latitude " + latitude + " and longitude " + longitude + ". Assume the following climate prevention technique is being used: " + climate_prevention_technique,
        config=types.GenerateContentConfig(
            system_instruction="You are a climate change simulation engine. You specialize in simulating the effects of climate change and human activities on satellite image descriptions in JSON format. Ensure that every word in the string is seperated by a space.\n\n",
            response_modalities=['TEXT'],
            response_mime_type="application/json",
            response_schema=ImageDescription
        ),
    )
    # print(response)
    return response.parsed.model_dump_json()

label_path = "/Users/kinjal/Code/UCB-AI-Hack-2025/930_056W_11S_930_chunk_0042.txt"
image_path = "/Users/kinjal/Code/UCB-AI-Hack-2025/930_056W_11S_930_chunk_0042.png"
button_label = "solar panel installation"
latitude = "11S"
longitude = "56W"

new_json = time_evolve_json_description(
    json_description=open(label_path, "r").read(),
    climate_prevention_technique=button_label,
    latitude=latitude,
    longitude=longitude
)

simulation_description = generate_modified_satellite_image(
    prompt=new_json,
    image_path=image_path,
    output_path="gemini_output.png"
)





# def generate_image(prompt, image_path, output_path='output.png', api_key=None):
#     """
#     Generate an image using Google's Gemini model based on a text prompt and an input image.
    
#     Args:
#         prompt (str): Text prompt to guide image generation
#         image_path (str): Path to the input image file
#         output_path (str): Path to save the generated image (default: 'output.png')
#         api_key (str, optional): Google AI API key. If not provided, will try to use GOOGLE_API_KEY environment variable.
    
#     Returns:
#         str: Path to the generated image if successful, None otherwise
#     """
#     try:
#         # Configure the API key
#         if api_key:
#             genai.configure(api_key=api_key)
        
#         # Initialize the model
#         model = genai.GenerativeModel('gemini-2.0-flash-vision')
        
#         # Read the input image
#         image_data = genai.upload_file(path=image_path)
        
#         # Generate content
#         response = model.generate_content([prompt, image_data])
        
#         # Extract the generated image (assuming it's in the response)
#         if hasattr(response, 'images') and response.images:
#             with open(output_path, 'wb') as f:
#                 f.write(response.images[0].getvalue())
#             return output_path
#         else:
#             print("No image was generated in the response")
#             return None
            
#     except GoogleAPIError as e:
#         print(f"Google API Error: {e}")
#         return None
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None

