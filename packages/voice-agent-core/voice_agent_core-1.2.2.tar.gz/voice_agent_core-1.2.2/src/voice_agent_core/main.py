# src/voice_agent_core/main.py

# Library entry point: exposes main functions for external use
from .listening import listen_for_speech
from .speaking import speak
from .llm import get_llm_response, send_tool_response_to_llm
from . import actions as toolbox

def get_tools():
    """Returns the set of available tools for use in external applications."""
    return {
        "play_on_youtube": toolbox.play_on_youtube,
        "pause_or_resume": toolbox.pause_or_resume,
        "stop_current_task": toolbox.stop_current_task,
        "open_vscode": toolbox.open_vscode,
        "open_website": toolbox.open_website,
        "search_google": toolbox.search_google,
        "get_weather": toolbox.get_weather,
    }

# Remove agent loop and CLI logic. This file now only exposes library functions.

class VoiceCompanionBot:
    """
    VoiceCompanionBot
    -----------------
    A customizable voice companion bot framework for Python.
    - Plug in any LLM handler (OpenAI, Gemini, etc.)
    - Use built-in voice tools or add your own
    - Suitable for conversational, helpful, and intelligent assistants

    Example usage:
        from voice_agent_core import VoiceCompanionBot
        def my_llm_handler(text):
            # Call your LLM API here and return a dict with 'type' and 'content' or 'call'
            ...
        bot = VoiceCompanionBot(llm_handler=my_llm_handler)
        bot.listen_and_respond()
    """
    def __init__(self, llm_handler, tools=None, speak_func=None, listen_func=None):
        """
        llm_handler: function that takes user text and returns a dict:
            {"type": "function_call", "call": {"name": ..., "args": {...}}}
            or
            {"type": "text_response", "content": ...}
        tools: dict of tool name to function (optional)
        speak_func: function to speak text (optional)
        listen_func: function to listen for speech (optional)
        """
        self.llm_handler = llm_handler
        self.tools = tools if tools is not None else get_tools()
        self.speak = speak_func if speak_func is not None else speak
        self.listen = listen_func if listen_func is not None else listen_for_speech

    def listen_and_respond(self):
        """
        Continuously listens for speech and responds using the LLM and available tools.
        Sends all user speech to the LLM handler for intelligent, conversational responses.
        """
        self.speak("I am ready. Say something!")
        while True:
            command = self.listen()
            if not command:
                self.speak("I didn't catch that. Please try again.")
                continue
            if "exit" in command or "goodbye" in command:
                self.speak("Goodbye!")
                break
            llm_decision = self.llm_handler(command)
            if llm_decision['type'] == 'function_call':
                tool_name = llm_decision['call']['name']
                tool_args = llm_decision['call'].get('args', {})
                if tool_name in self.tools:
                    try:
                        result = self.tools[tool_name](**tool_args)
                        self.speak(str(result))
                    except Exception as e:
                        self.speak(f"Error using {tool_name}: {e}")
                else:
                    self.speak(f"Unknown tool: {tool_name}")
            elif llm_decision['type'] == 'text_response':
                self.speak(llm_decision['content'])
            else:
                self.speak("Sorry, I didn't understand the response.")