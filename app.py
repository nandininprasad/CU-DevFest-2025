import os
import sqlite3
import datetime
import wave
import sounddevice as sd
import numpy as np
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import openai
from PIL import Image
from io import BytesIO
import requests

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API"))

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('transcriptions.db')
cursor = conn.cursor()

import sqlite3

# Connect to your database
conn = sqlite3.connect('transcriptions.db')
cursor = conn.cursor()

# Check if the 'image_path' column exists
cursor.execute("PRAGMA table_info(transcriptions);")
columns = [column[1] for column in cursor.fetchall()]

if 'image_path' not in columns:
    # Add the 'image_path' column
    cursor.execute("ALTER TABLE transcriptions ADD COLUMN image_path TEXT;")
    conn.commit()

conn.close()


conn = sqlite3.connect('transcriptions.db')
cursor = conn.cursor()


# Create a table to store transcriptions, summaries, image paths, and timestamps
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transcriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transcription TEXT,
        summary TEXT,
        image_path TEXT,
        timestamp TEXT
    )
''')
conn.commit()

def record_audio(filename="recorded_audio.wav", duration=5, sample_rate=44100):
    """Records audio and saves it as a WAV file."""
    st.info("🎙️ Recording... Speak now!")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())
    st.success("✅ Recording complete!")
    return filename

def transcribe_audio(filename):
    """Transcribes audio using Groq's Speech-to-Text API."""
    with open(filename, "rb") as file:
        transcription = groq_client.audio.transcriptions.create(
            file=(filename, file.read()),
            model="whisper-large-v3-turbo"
        )
        return transcription.text

def summarize_text(text):
    """Summarizes text using OpenAI's GPT model."""
    client = openai.OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarize the following text strictly. You are taking a notes like a doctor, but do not make any mention of your role. You take the role of an apathetic, narrator. Don't refer to the person as a subject. if a person reports running from a bear, you should say 'Ran from a bear', possibly in the present tense, as a description of a dream. You are transcribing  a dream journal"},
            {"role": "user", "content": text}
        ]
    )
    return completion.choices[0].message.content

def generate_image_from_text(prompt):
    """Generates an image from a text prompt using OpenAI's DALL·E API."""
    client = openai.OpenAI()
    response = client.images.generate(
    prompt=prompt,
    n=2,
    size="1024x1024"
    )   
    print(response)
    image_url = response.data[0].url
    image_response = requests.get(image_url)
    image = Image.open(BytesIO(image_response.content))
    return image

def save_to_database(transcription, summary, image_path):
    """Saves the transcription, summary, and image path to the SQLite database with a timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO transcriptions (transcription, summary, image_path, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (transcription, summary, image_path, timestamp))
    conn.commit()



def fetch_entries_by_date(date):
    """Fetches entries from the database for a specific date."""
    cursor.execute('''
        SELECT transcription, summary, image_path, timestamp FROM transcriptions
        WHERE DATE(timestamp) = ?
    ''', (date,))
    return cursor.fetchall()

st.title("Tranquili-Tea: Dream Journal 🌙🎙️")

# Initialize session state for button control
if "recording" not in st.session_state:
    st.session_state.recording = False

# Duration selection
duration = st.slider("⏱️ Recording Duration (seconds)", min_value=2, max_value=15*60, value=10)

# Record button
if st.button("🎙️ Start Recording", disabled=st.session_state.recording):
    st.session_state.recording = True
    filename = record_audio(duration=duration)
    st.session_state.recording = False

    st.info("🔄 Transcribing... Please wait.")
    with st.spinner("Transcribing..."):
        transcription = transcribe_audio(filename)

    if transcription:
        st.success("✅ Transcription Complete!")
        st.write(f"**You said:** {transcription}")

        st.info("🔄 Summarizing... Please wait.")
        with st.spinner("Summarizing..."):
            summary = summarize_text(transcription)
        st.success("✅ Summarization Complete!")
        st.write(f"**Summary:** {summary}")

        st.info("🖼️ Generating Image... Please wait.")
        with st.spinner("Generating Image..."):
            image = generate_image_from_text(summary)
            image_path = f"generated_images/{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image.save(image_path)
        st.success("✅ Image Generation Complete!")
        st.image(image, caption="Generated Image")

        # Save transcription, summary, and image path to the database
        save_to_database(transcription, summary, image_path)
    else:
        st.error("⚠️ No speech detected. Please try again.")

    # Clean up
    os.remove(filename)

# Date input for fetching entries
st.header("📅 View Entries by Date")
selected_date = st.date_input("Select a date to view entries:")
if st.button("Fetch Entries"):
    entries = fetch_entries_by_date(selected_date.strftime("%Y-%m-%d"))
    if entries:
        for transcription, summary, image_path, timestamp in entries:
            st.write(f"**Timestamp:** {timestamp}")
            st.write(f"**Transcription:** {transcription}")
            st.write(f"**Summary:** {summary}")
            
            # Check if image_path is not None or empty before using os.path.exists
            if image_path and os.path.exists(image_path):
                image = Image.open(image_path)
                st.image(image, caption="Generated Image")
            else:
                st.write("Image not found or path is invalid.")
            
            st.write("---")
    else:
        st.write("No entries found for the selected date.")