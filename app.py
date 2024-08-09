import streamlit as st
from openai import OpenAI
import openai
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from io import BytesIO

# Load environment variables
load_dotenv()

# Set up OpenAI API key
gpt_key = openai.api_key = os.getenv("OPENAI_API_KEY")

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def generate_affirmation(responses):
    prompt = f"""Based on these responses about someone's life:
    1. The user's name is: {responses[0]}
    2. {responses[1]}
    3. {responses[2]}
    4. {responses[3]}
    Generate a positive, uplifting personal affirmation that is at least 150 words long. Be sure to greet
    the user based on their name, and use their name where appropriate for a personal touch.
    The affirmation should be encouraging and inspirational, suitable for a few minutes of reflection."""

    client = OpenAI(api_key=gpt_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates personalized affirmations."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4096,
    )
    return response.choices[0].message.content

def text_to_speech(text):
    audio_generator = client.generate(
        text=text,
        voice="KmnvDXRA0HU55Q0aqkPG",  # Nicole
        model="eleven_multilingual_v2"
    )
    
    # Convert generator to bytes
    audio_bytes = BytesIO()
    for chunk in audio_generator:
        audio_bytes.write(chunk)
    audio_bytes.seek(0)
    
    return audio_bytes

st.title("Personal Affirmation Generator")

# Initialize session state
if 'stage' not in st.session_state:
    st.session_state.stage = 0
if 'responses' not in st.session_state:
    st.session_state.responses = []
if 'affirmation' not in st.session_state:
    st.session_state.affirmation = ""

# Questions to ask
questions = [
    "What's your name?",
    "What's a recent accomplishment you're proud of?",
    "What's a personal challenge you're currently facing?",
    "What's a long-term goal you're working towards?"
]

# Chat interface
if st.session_state.stage < 4:
    with st.form(key=f"form_{st.session_state.stage}"):
        st.write(f"{questions[st.session_state.stage]}")
        user_input = st.text_input("Your response:", key=f"question_{st.session_state.stage}")
        next_button = st.form_submit_button("Next")
        if next_button:
            st.session_state.responses.append(user_input)
            st.session_state.stage += 1
            st.rerun()

if st.session_state.stage == 4 and not st.session_state.affirmation:
    with st.spinner("Generating your personalized affirmation..."):
        st.session_state.affirmation = generate_affirmation(st.session_state.responses)
        st.session_state.stage += 1
        st.rerun()

if st.session_state.affirmation:
    st.write("Your Personalized Affirmation:")
    st.write(st.session_state.affirmation)
    
    if st.button("Listen to Affirmation"):
        with st.spinner("Generating audio... Turn your speakers up!"):
            audio = text_to_speech(st.session_state.affirmation)
            st.audio(audio, format='audio/mp3')  # Assuming the generated audio is in MP3 format
    
    if st.button("Start Over"):
        st.session_state.stage = 0
        st.session_state.responses = []
        st.session_state.affirmation = ""
        st.rerun()
