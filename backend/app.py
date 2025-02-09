from flask import Flask, request, jsonify, send_file
import base64
import subprocess
import io
from PIL import Image
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

groq_client = Groq(
    api_key=os.getenv("GROQ_API")
)

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def downsample_image(image_bytes, max_size_kb=1000, quality=50):
    """ Convert image to JPEG, reduce quality, and resize if needed. """
    
    image = Image.open(io.BytesIO(image_bytes))

    # Convert to RGB (if it's a PNG with transparency)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    # First compression attempt
    img_io = io.BytesIO()
    image.save(img_io, format="JPEG", quality=quality)
    
    # Check file size
    if img_io.tell() / 1024 <= max_size_kb:
        return img_io.getvalue()  # Return compressed image

    # If still too large, resize
    width, height = image.size
    scale_factor = (max_size_kb * 1024) / img_io.tell()
    new_size = (int(width * scale_factor**0.5), int(height * scale_factor**0.5))
    
    image = image.resize(new_size, Image.ANTIALIAS)
    
    # Save again with reduced size
    img_io = io.BytesIO()
    image.save(img_io, format="JPEG", quality=quality)
    
    return img_io.getvalue()  # Return the final downsampled image

OUTPUT_FOLDER = "./"
global state
state = []

@app.route("/api/process-image", methods=["GET", "POST"])
def process_image():
    global state
    data = request.json
    image_data = data.get("image")

    if not image_data:
        print("No image received")
        return jsonify({"error": "No image received"}), 400
    
    image_data = image_data.split(",")[1]  # Remove "data:image/png;base64,"
    image_bytes = base64.b64decode(image_data)
    downsampled_image = downsample_image(image_bytes)
    encoded_image = base64.b64encode(downsampled_image).decode('utf-8')
    new_message = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "In less than 20 words, describe this image like Gordon Ramsay would!",
             },
             {
                 "type": "image_url",
                 "image_url": {
                     "url": f"data:image/jpeg;base64,{encoded_image}"
                 },
             },
        ],
    }

    state.append(new_message)
    state = state[-10:]

    # chat_completion = groq_client.chat.completions.create(
    #     messages = [new_message],
    #     model="llama-3.2-11b-vision-preview"
    # )
    
    # print(chat_completion.choices[0].message.content)
    print("Groq response acquired")
    return generate_audio()


def generate_audio():
    
    try:
        
        text = "this is coming from a flask you donkey"
        output_path = OUTPUT_FOLDER + "output.mp3"
        # subprocess.run(["python3", "tts.py", text, output_path])
        
        return send_file(output_path, mimetype="audio/mpeg", as_attachment=False)
    
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"TTS script failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

    


if __name__ == "__main__":
    app.run(debug=True)

