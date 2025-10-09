# src/voice_agent_core/actions.py

import pywhatkit
import webbrowser
import pyautogui
import subprocess
import os
import requests

def play_on_youtube(query: str):
    """
    Opens YouTube and plays the given video or song query.
    If the user does not specify what to play, the model should ask for a query.

    Args:
        query (str): The name of the song or video to play. For example: 'lofi hip hop radio'
    """
    try:
        pywhatkit.playonyt(query)
        return f"Now playing '{query}' on YouTube."
    except Exception as e:
        return f"Sorry, I couldn't play that. Error: {e}"

def pause_or_resume():
    """Pauses or resumes the currently playing media by simulating a spacebar press."""
    pyautogui.press('space')
    return "Done."

def stop_current_task():
    """Stops the current task by closing the active tab in the browser (Ctrl+W)."""
    pyautogui.hotkey('ctrl', 'w')
    return "Stopped."

def open_website(url: str):
    """
    Opens a website in the default browser given a valid URL.

    Args:
        url (str): The full URL of the website to open. Must start with http or https.
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    webbrowser.open(url)
    return f"Opening {url}."

def search_google(query: str):
    """
    Searches for a query on Google.

    Args:
        query (str): The topic or question to search for on Google.
    """
    pywhatkit.search(query)
    return f"Searching Google for '{query}'."

def open_vscode():
    """Opens the Visual Studio Code application."""
    try:
        subprocess.run(['code'], check=True)
        return "Opening Visual Studio Code."
    except FileNotFoundError:
        return "I couldn't find Visual Studio Code. Is it installed and in your system's PATH?"
    except Exception as e:
        return f"An error occurred: {e}"

def get_weather(location: str):
    """
    Fetches the current weather for a specified location using the OpenWeatherMap API.

    Args:
        location (str): The city name to get the weather for. For example: 'London' or 'Tokyo'
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Weather API key is not configured. I can't check the weather."
            
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": location, "appid": api_key, "units": "metric"}
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        weather_data = response.json()
        
        if weather_data.get("cod") != 200:
            return f"Sorry, I couldn't find the weather for {location}."

        city = weather_data["name"]
        description = weather_data["weather"][0]["description"]
        temperature = weather_data["main"]["temp"]
        
        return f"The weather in {city} is currently {temperature:.0f} degrees Celsius with {description}."

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            return f"I'm sorry, I couldn't find a city named {location}."
        return f"An HTTP error occurred while fetching the weather: {http_err}"
    except Exception as e:
        return f"An error occurred while fetching the weather: {e}"