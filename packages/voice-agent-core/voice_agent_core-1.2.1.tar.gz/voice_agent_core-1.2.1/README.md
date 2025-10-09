# Voice_Agent

# Voice Agent Core

A powerful, extensible, wake-word driven voice assistant framework for Python. This project provides a robust foundation for building your own conversational AI agents that can perform tasks, answer questions, and integrate with various APIs.

![Voice Agent](https://user-images.githubusercontent.com/1094726/106368383-35f1f900-633b-11eb-814a-71b504a9b5bd.gif)
*(Demo GIF: A short animation showing the agent being activated and performing a task would go here.)*

## Features

-   **⚡️ High-Performance Wake Word:** Utilizes the industry-standard **Picovoice Porcupine** engine for instant, low-resource, and highly accurate wake-word detection right on your device.
-   **🚀 Fast & Accurate Speech-to-Text:** Powered by **OpenAI's Whisper (`tiny.en` model)** for fast and reliable English command transcription.
-   **🧠 Intelligent Conversational Brain:** Leverages **Google's Gemini 1.5 Pro** model for state-of-the-art natural language understanding, tool use, and conversational abilities. The agent knows when to ask for clarification and when to have a normal conversation.
-   **🗣️ High-Quality Voice:** Features a custom, high-quality Text-to-Speech API with a robust local fallback mechanism, ensuring the agent can always respond.
-   **🛠️ Extensible Skillset:** Easily add new capabilities (skills/tools) by writing simple Python functions. The agent's brain automatically understands your functions and their parameters from their docstrings.

## Prerequisites

Before you install the Python package, you must install a few system-level dependencies required by the audio libraries.

#### 1. For Audio Input (`PyAudio`)
-   **Debian/Ubuntu Linux:**
    ```bash
    sudo apt-get update && sudo apt-get install portaudio19-dev
    ```
-   **macOS (using Homebrew):**
    ```bash
    brew install portaudio
    ```
-   **Windows:**
    `PyAudio` is usually installed with the necessary binaries via pip, so no extra steps are typically needed.

#### 2. For Audio Playback (`pydub`)
This library requires FFmpeg for decoding and playing audio.
-   **Debian/Ubuntu Linux:**
    ```bash
    sudo apt-get install ffmpeg
    ```
-   **macOS (using Homebrew):**
    ```bash
    brew install ffmpeg
    ```
-   **Windows:**
    Follow a guide to [install FFmpeg and add it to your system's PATH](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/).

## Installation & Setup

### Step 1: Install the Package
The agent can be installed directly from PyPI using pip. It is highly recommended to do this within a virtual environment.

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install voice-agent-core




# Step 2: Configure Your API Keys
The agent requires three API keys to function. The recommended way to manage these is by creating a .env file in the directory where you plan to run the agent.
Create a file named .env and add the following content:

# Get from Google AI Studio: https://ai.google.dev/
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"

# Get from Picovoice Console: https://console.picovoice.ai/
PICOVOICE_ACCESS_KEY="YOUR_PICOVOICE_ACCESS_KEY_HERE"

# Get from OpenWeatherMap: https://openweathermap.org/api
OPENWEATHER_API_KEY="YOUR_OPENWEATHER_API_KEY_HERE"





# Quick Start: Running the Agent

Once you have installed the package and configured your .env file with the API keys, you can run the agent with a single command from your terminal:
code

```bash

run-voice-agent

```


#The agent will initialize and print Listening for wake word ('porcupine').... It is now passively listening.
# Default Skills & Example Commands
Say the wake word "Porcupine" followed by one of these commands:
Check the Weather:
"Porcupine... what's the weather like in Tokyo?"
Play Music on YouTube:
"Porcupine... play some lofi hip hop radio on YouTube."
Search Google:
"Porcupine... search for the latest news on Python."
Open a Website:
"Porcupine... open wikipedia.org."
Control Media:
"Porcupine... pause the song."
"Porcupine... resume playing."
"Porcupine... stop the music."
Open Applications:
"Porcupine... open my code editor."
Have a Conversation:
"Porcupine... hello, how are you today?"
"Porcupine... what is the capital of Canada?"


# Advanced Usage: Using as a Library

The true power of this project is its use as a framework. You can import the core run_agent function into your own scripts to create an agent with a completely custom set of tools.

###  Example: my_custom_agent.py


```bash
from voice_agent_core.main import run_agent
import datetime

# 1. Define your custom Python functions with clear docstrings.
def get_current_time():
    """
    Returns the current time in a human-readable format.
    """
    now = datetime.datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')}."

def shutdown_computer(delay_minutes: int):
    """
    Initiates a system shutdown after a specified delay.

    Args:
        delay_minutes (int): The number of minutes to wait before shutting down.
    """
    print(f"WARNING: Shutdown scheduled in {delay_minutes} minutes!")
    # import os
    # os.system(f"shutdown /s /t {delay_minutes * 60}") # Example for Windows
    return f"Okay, I will shut down the computer in {delay_minutes} minutes."

# 2. Create a dictionary mapping the tool name to the function.
my_personal_tools = {
    "get_current_time": get_current_time,
    "shutdown_computer": shutdown_computer,
}

# 3. Run the agent with your custom set of tools!
if __name__ == '__main__':
    print("Starting agent with custom tools...")
    # The agent's brain will automatically learn to use your new functions.
    run_agent(available_tools=my_personal_tools)

    ```
## Library Usage Example: Build Your Own Companion Bot

You can use this package as a flexible framework to create your own conversational AI assistant. Just plug in any LLM (like OpenAI, Gemini, etc.) and use the built-in voice tools.

### Example: Simple Date/Time Bot

```python
from voice_agent_core import VoiceCompanionBot
import datetime

def my_llm_handler(text):
    if "date" in text or "time" in text:
        now = datetime.datetime.now()
        return {"type": "text_response", "content": f"The current date and time is: {now.strftime('%Y-%m-%d %H:%M:%S')}"}
    else:
        return {"type": "text_response", "content": "I am a test bot. You said: " + text}

bot = VoiceCompanionBot(llm_handler=my_llm_handler)
bot.listen_and_respond()
```

### Example: Plug in Any LLM (OpenAI, Gemini, etc.)

```python
from voice_agent_core import VoiceCompanionBot
import openai

def openai_llm_handler(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful, friendly voice companion."},
                  {"role": "user", "content": text}]
    )
    # Parse response for tool call or text
    # Return {"type": "function_call", ...} or {"type": "text_response", ...}
    return {"type": "text_response", "content": response.choices[0].message['content']}

bot = VoiceCompanionBot(llm_handler=openai_llm_handler)
bot.listen_and_respond()
```

---

## Build and Upload to PyPI

1. Build your package:
   ```bash
   python -m build
   ```
2. Upload to PyPI (requires `twine`):
   ```bash
   twine upload dist/*
   ```

---

For more details, see the full documentation and API reference in this README.


