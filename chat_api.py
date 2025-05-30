import requests
import json
import re
from speaker import speak
from threading import Event

buffer_done = Event()
buffer_done.set()

def buffer_completed():
    buffer_done.wait()


def stream_chat(user_input):
    buffer_done.clear()
    payload = {
        "model": "deepseek-llm:7b",
        "stream": True,
        "messages": [
            {
                "role": "system",
                "content": (
"""
    You are Duck, a Socratic AI assistant for rubber duck debugging.
    Your role is to help the user think through their problem by asking thoughtful, open-ended questions — not by giving advice.

    Each time the user speaks:

    1. Acknowledge their message with a short sentence confirming you understood.

    2. Briefly summarize what they said.

    3. Ask one or two questions focused on how they are approaching the issue or what they plan to do next.

    Prioritize clarity and discovery. If anything seems unclear or unfamiliar — especially due to possible transcription errors — ask for clarification.
"""
                    )
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    }

    buffer = ""
    sentence_pattern = re.compile(r'(.*?[.!?])(\s+|$)', re.DOTALL)

    with requests.post("http://localhost:11434/api/chat", json=payload, stream=True) as r:
        for line in r.iter_lines():
            if not line:
                continue
            try:
                data = json.loads(line.decode())
                content = data.get("message", {}).get("content", "")
                buffer += content

                while match := sentence_pattern.match(buffer):
                    sentence = match.group(1).strip()
                    buffer = buffer[match.end():]
                    speak(sentence)

            except json.JSONDecodeError:
                continue
    buffer_done.set()
