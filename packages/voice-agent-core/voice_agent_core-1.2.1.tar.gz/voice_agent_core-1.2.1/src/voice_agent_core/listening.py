# src/voice_agent_core/listening.py

import os
import sys
import struct
import pyaudio
import speech_recognition as sr
from contextlib import contextmanager

@contextmanager
def suppress_stderr():
    """A context manager to temporarily suppress stderr messages."""
    original_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    try:
        yield
    finally:
        sys.stderr.close()
        sys.stderr = original_stderr

def listen_for_speech():
    """
    Listens for any speech using the microphone and returns the transcribed text.
    This function is suitable for conversational bots, not just command-based ones.
    """
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 2.0

    with sr.Microphone() as source:
        print("Adjusting for noise...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening for speech...")
        
        try:
            with suppress_stderr():
                audio = recognizer.listen(source, timeout=15, phrase_time_limit=15)
            
            print("Transcribing with 'tiny.en' model...")
            command = recognizer.recognize_whisper(audio, language="english", model="tiny.en")
            print(f"Heard: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError as e:
            print(f"Whisper service error: {e}")
            return None