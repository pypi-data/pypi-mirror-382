# Voice Agent Core

A flexible, conversational voice companion bot framework for Python. Easily build your own AI assistant by plugging in any LLM (OpenAI, Gemini, etc.) and using built-in voice tools. Great for personal productivity, home automation, or just having a friendly AI to talk to!

## Features
- **Conversational AI:** Integrate any LLM (OpenAI, Gemini, etc.) for smart, natural conversations.
- **Speech Recognition:** Uses Whisper and SpeechRecognition for accurate voice input.
- **Text-to-Speech:** Responds with high-quality voice using TTS APIs and local fallback.
- **Extensible Tools:** Add your own Python functions as tools (play music, check weather, control apps, etc.).
- **Easy API:** Just provide an LLM handler and start your bot!

## Requirements
- Python 3.8+
- System dependencies for audio:
  - **Linux:** `sudo apt-get install portaudio19-dev ffmpeg`
  - **macOS:** `brew install portaudio ffmpeg`
  - **Windows:** Install [FFmpeg](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/) and ensure it's in your PATH.

## Installation
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install voice-agent-core
```

## Quick Start: Your Own Companion Bot
Create a Python file (e.g., `my_bot.py`):
```python
from voice_agent_core import VoiceCompanionBot
import datetime

def my_llm_handler(text):
    if "date" in text or "time" in text:
        now = datetime.datetime.now()
        return {"type": "text_response", "content": f"The current date and time is: {now}"}
    else:
        return {"type": "text_response", "content": "I am your companion bot! You said: " + text}

bot = VoiceCompanionBot(llm_handler=my_llm_handler)
bot.listen_and_respond()
```
Run it:
```bash
python my_bot.py
```
Speak to your bot! It will respond with the date/time or echo your message.

## Advanced: Use Any LLM (OpenAI Example)
```python
from voice_agent_core import VoiceCompanionBot
import openai

def openai_llm_handler(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful, friendly voice companion."},
                  {"role": "user", "content": text}]
    )
    return {"type": "text_response", "content": response.choices[0].message['content']}

bot = VoiceCompanionBot(llm_handler=openai_llm_handler)
bot.listen_and_respond()
```

## Adding Custom Tools
You can add your own Python functions as tools. For example:
```python
def get_weather(location):
    # Your weather API logic here
    return f"Weather in {location}: Sunny!"

tools = {"get_weather": get_weather}
bot = VoiceCompanionBot(llm_handler=my_llm_handler, tools=tools)
```
Your LLM handler should return:
```python
{"type": "function_call", "call": {"name": "get_weather", "args": {"location": "London"}}}
```
The bot will call your tool and speak the result.

## API Overview
- `VoiceCompanionBot(llm_handler, tools=None, speak_func=None, listen_func=None)`
  - `llm_handler(text)`: function that takes user speech and returns a dict:
    - `{ "type": "function_call", "call": {"name": ..., "args": {...}} }`
    - `{ "type": "text_response", "content": ... }`
  - `tools`: dict of tool name to function (optional)
  - `speak_func`: custom TTS function (optional)
  - `listen_func`: custom speech recognition function (optional)
- `bot.listen_and_respond()`: starts the main loop


## License
MIT

---
For more details, see the API reference and examples above. Enjoy building your own AI companion!


