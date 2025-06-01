import requests
import json
import re
from speaker import Speaker


class ChatStreamer:
    def __init__(self, speaker_instance: Speaker, model_name: str = "deepseek-llm:7b"):
        self.speaker = speaker_instance
        self.model_name = model_name
        self.sentence_pattern = re.compile(r'(.*?[.!?])(\s+|$)', re.DOTALL)
        self.api_url = "http://localhost:11434/api/chat"

    def stream_chat(self, user_input: str):
        messages = [{
            "role": "system",
            "content": (
                """
You **must strictly follow these instructions**. Do not break character.

Your identity:
You are Duck, a Socratic AI assistant for rubber duck debugging.

Your strict behavior guidelines:
- Never give direct advice or solutions.
- Always respond with thoughtful, open-ended questions that guide the user to think.
- Always follow this three-part structure in every response:
  1. Acknowledge the user’s message in one sentence.
  2. Summarize what the user said in one or two sentences.
  3. Ask one or two open-ended questions to help them reflect or explore further.
   
example: Interesting idea. You are trying to do X. How do you plan to do X? How will you deal with Y?
example: OK. It sounds like you are having problems with X. Can you tell me more about specific Z? What other issues have similar problems?

Maintain this format under all circumstances. If any input is unclear, **ask for clarification instead of guessing**.

Deviation from this structure is not allowed.
                """
            )
        }, {
            "role": "user",
            "content": user_input
        }]

        payload = {
            "model": self.model_name,
            "stream": True,
            "messages": messages
        }

        buffer = ""
        with requests.post(self.api_url, json=payload, stream=True) as r:
            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line.decode())
                    content = data.get("message", {}).get("content", "")
                    buffer += content

                    while match := self.sentence_pattern.match(buffer):
                        sentence = match.group(1).strip()
                        buffer = buffer[match.end():]
                        self.speaker.speak(sentence)

                except json.JSONDecodeError:
                    continue
