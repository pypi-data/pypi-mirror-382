# src/voice_agent_core/speaking.py

# Make TTS functions modular and remove agent-specific print statements
import pyttsx3
from pydub import AudioSegment
from pydub.playback import play
import requests
import io
import base64

TTS_ENDPOINT_URL = "https://sasthra.in/tts"

# Initialize the fallback engine once
try:
    fallback_engine = pyttsx3.init()
except Exception:
    fallback_engine = None

def speak_with_fallback(text):
    """A simple, local text-to-speech fallback."""
    if fallback_engine:
        fallback_engine.say(text)
        fallback_engine.runAndWait()

def speak(text):
    """
    Sends text to the custom TTS endpoint, decodes the response, and plays the audio.
    Falls back to a local TTS if the API fails.
    """
    try:
        response = requests.post(TTS_ENDPOINT_URL, json={'text': text}, timeout=20)
        response.raise_for_status()

        json_response = response.json()
        
        if 'audio' in json_response and json_response['audio']:
            audio_base64 = json_response['audio']
            audio_data = base64.b64decode(audio_base64)
            
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
            play(audio_segment)
        else:
            speak_with_fallback(text)
    except requests.exceptions.RequestException:
        speak_with_fallback(text)
    except (KeyError, base64.binascii.Error, Exception):
        speak_with_fallback(text)