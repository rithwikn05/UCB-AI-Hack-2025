from flask import Flask, render_template, request, jsonify, url_for
import replicate
import os

app = Flask(__name__)

# Placeholder for button labels (could be dynamically set by REST API later)
button_labels = ["Wildfire", "Flood", "Earthquake", "Hurricane"]

@app.route('/')
def index():
    # Try to get the latest image if exists
    image_path = None
    output_dir = os.path.join(app.static_folder, "outputs")
    if os.path.exists(output_dir):
        images = sorted(
            [f for f in os.listdir(output_dir) if f.endswith(".png")],
            key=lambda x: os.path.getmtime(os.path.join(output_dir, x)),
            reverse=True
        )
        if images:
            image_path = f"outputs/{images[0]}"

    return render_template('index.html', button_labels=button_labels, image_path=image_path)

@app.route('/disaster', methods=['POST'])
def disaster():
    data = request.get_json()
    disaster_type = data.get('disaster')

    prompt = f"an ariel view of a landscape that has been affected by {disaster_type}. Make it zoom out and realistic."
    input_data = {
        "prompt": prompt,
        "scheduler": "K_EULER"
    }

    try:
        output = replicate.run(
            "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
            input=input_data
        )

        output_dir = os.path.join("static", "outputs")
        os.makedirs(output_dir, exist_ok=True)

        latest_image = None
        for index, item in enumerate(output):
            image_filename = f"output_{index}.png"
            image_path = os.path.join(output_dir, image_filename)
            with open(image_path, "wb") as file:
                file.write(item.read())
            latest_image = f"outputs/{image_filename}"

        return jsonify({"status": "image generated", "disaster": disaster_type, "image_path": latest_image})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)