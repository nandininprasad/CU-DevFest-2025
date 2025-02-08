import websockets
import asyncio
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from pydub import AudioSegment
from pydub.utils import which
from pydub.playback import play
import io
import json
import sys

AudioSegment.converter = which("ffmpeg")  # Set ffmpeg path
AudioSegment.ffprobe = which("ffprobe") 
load_dotenv()

# send auth post request 

PLAYHT_API_KEY = os.getenv("PLAYHT_API_KEY")
PLAYHT_USER_ID = os.getenv("PLAYHT_USER_ID")

def auth():
    url = "https://api.play.ht/api/v4/websocket-auth"
    headers = {
        "Authorization": "Bearer " + PLAYHT_API_KEY,
        "X-User-Id"    : PLAYHT_USER_ID,
        "Content-Type" : "application/json"
        }
    
    response = requests.post(url, headers=headers)

    return response.json()


response = auth()

voice_dict = {
    "GordonRamsay": "s3://voice-cloning-zero-shot/1806c2a9-2c23-4336-93a5-5447b80295e9/original/manifest.json",
}

async def handle_request(text, model, voice="GordonRamsay"):
    # takes input text, passes it to tts model, receives audio file over websocket
    
    global response

    expiry_date = datetime.strptime(response["expires_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
    current_date = datetime.now()
    # if time diff is less than an hour, renew token
    if (expiry_date - current_date).seconds < 3600:
        response = auth()

    url = response['websocket_urls'][model]



    request = {
         "text": text, # less than 20k characters
         "voice": voice_dict["GordonRamsay"], #GordonRamsay clone
         "output_format": "mp3",
         "temperature": "0.7",
         "speed": "1.0",
    }

    audio_chunks = []

    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(request))
        while True:
            message = await websocket.recv()

            if isinstance(message, bytes):
                    # Received audio chunk
                    audio_chunks.append(message)
            else:
                # Received a JSON message
                data = json.loads(message)

                if data.get("type") == "start":
                    print(f"Processing started. Request ID: {data.get('request_id')}")

                elif data.get("type") == "end":
                    print(f"Processing ended. Request ID: {data.get('request_id')}")
                    break

        # Combine received audio chunks
        audio_data = b"".join(audio_chunks)

        # DEBUG: Save raw audio file to check format
        with open("output_raw.mp3", "wb") as f:
            f.write(audio_data)
        print("Raw audio saved as output_raw.mp3")

        # Convert binary data into an audio segment
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")

        # Save or play the audio
        audio_segment.export("output.mpeg", format="mp3")

        # Play the audio
        play(audio_segment)
        print("Audio saved as output.mpeg")

model = "PlayDialog"


text = sys.argv[1]

asyncio.get_event_loop().run_until_complete(handle_request(text, model))
    