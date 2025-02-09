from flask import Flask, request, jsonify, send_file
import base64
import subprocess
import io
from PIL import Image
import os
from groq import Groq
from dotenv import load_dotenv
import random

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

@app.route("/api/process-image", methods=["POST"])
def process_image():
    global state
    data = request.json
    image_data = data.get("screenImage")
    webcam_image = data.get("webcamImage")
    coach = data.get("coach")
    print("Coach: ", coach)
    if not image_data:
        print("No image received")
        return jsonify({"error": "No image received"}), 400
    
    image_data = image_data.split(",")[1]  # Remove "data:image/png;base64,"
    image_bytes = base64.b64decode(image_data)
    downsampled_image = downsample_image(image_bytes, max_size_kb=1024*10)
    encoded_image = base64.b64encode(downsampled_image).decode('utf-8') 
    
    webcam_image = webcam_image.split(",")[1]  # Remove "data:image/png;base64,"
    webcam_image = base64.b64decode(webcam_image)
    webcam_image = downsample_image(webcam_image, max_size_kb=1024*10)
    webcam_image = base64.b64encode(webcam_image).decode('utf-8') 


    llama_message = {

        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "You are looking at a screen of a laptop. Describe any details that might pertain to whether the person is working or wasting time/ indulging in entertainment."
             },
             {
                 "type": "image_url",
                 "image_url": {
                     "url": f"data:image/jpeg;base64,{encoded_image}"
                 },
             },
        ],
    }


    chat_completion = groq_client.chat.completions.create(
        messages = [llama_message],
        model="llama-3.2-11b-vision-preview"
    )
    
    response1 = chat_completion.choices[0].message.content
    print("Grok analysis: ", response1)

    llama_message = {

        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "You are looking at a webcam feed from a laptop. Describe any details that might pertain to whether the person is working or wasting time/ indulging in entertainment."
             },
             {
                 "type": "image_url",
                 "image_url": {
                     "url": f"data:image/jpeg;base64,{webcam_image}"
                 },
             },
        ],
    }


    chat_completion = groq_client.chat.completions.create(
        messages = [llama_message],
        model="llama-3.2-11b-vision-preview"
    )
    
    response2 = chat_completion.choices[0].message.content
    print("Grok analysis2: ", response2)



    new_message = {

        "role": "user",
        "content": f"""Image description: r{response1}. Webcam descripton: {response2}. These descriptions are from a different model. You are {coach}: a strict, no-nonsense motivator with snark but zero offensive language.
According to the image description answer the following:
1. If you see evidence the person is NOT working or studying (e.g. using social media, on their phone, looking totally distracted), then respond in 20 words or fewer with a snarky Gordon Ramsay-style command that tells them to get back to work—but without using any offensive or explicit words.
If they are on any kind of social media, on their phone, or looking totally distracted, you should scold them.
2. If you see they are obviously working or studying, reply with the word "NO" (no quotes).
3. If you cannot tell if they are on social media and wasting time  whether they are wasting time or not, reply EXACTLY with the word "NO" (no quotes).

All these rules are STRICT. 
- Maximum 20 words if you scold them.  
- "NO" if they're working"""
        
    }


    chat_completion = groq_client.chat.completions.create(
        messages = [new_message],
        model="deepseek-r1-distill-llama-70b"
    )

    response = chat_completion.choices[0].message.content
    deeseek_think = response.split("</think>")[0]
    print("Deepseek analysis: ", deeseek_think)
    response = response.split("</think>")[1].lstrip().rstrip()
    print(response)

    try:
        if len(response) > 0 and response != "NO":
            print("Coach 2:", coach)
            # text = response
            # output_path = OUTPUT_FOLDER + "output.mp3"


            # print(output_path)
            # subprocess.run(["python3", "tts.py", text, output_path])

            if coach == "Gordon Ramsay":
                path = "./gordonRamsay/"
                mp3_list = os.listdir(path)
                mp3_list = [path + mp3 for mp3 in mp3_list]
                #Choose randomly
                mp3 = random.choice(mp3_list)
            else:
                path = "./davidGoggins/"
                mp3_list = os.listdir(path)
                mp3_list = [path + mp3 for mp3 in mp3_list]
                #Choose randomly
                mp3 = random.choice(mp3_list)


            print("We sending th efile")
            return send_file(mp3, mimetype="audio/mpeg", as_attachment=False)
        
        return "", 204
    
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"TTS script failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500




if __name__ == "__main__":
    app.run(debug=True)

