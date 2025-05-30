import threading

import requests
import json
import re
from speaker import speak

messages = [
    {
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
    }
]

def stream_chat(user_input):
    global messages
    messages.append({
        "role": "user",
        "content": user_input
    })

    payload = {
        "model": "deepseek-llm:7b",
        "stream": True,
        "messages": messages
    }

    buffer = ""
    sentence_pattern = re.compile(r'(.*?[.!?])(\s+|$)', re.DOTALL)
    print(payload)
    with requests.post("http://localhost:11434/api/chat", json=payload, stream=True) as r:
        response_content = ""
        for line in r.iter_lines():
            if not line:
                continue
            try:
                data = json.loads(line.decode())
                content = data.get("message", {}).get("content", "")
                buffer += content
                response_content += content

                while match := sentence_pattern.match(buffer):
                    sentence = match.group(1).strip()
                    buffer = buffer[match.end():]
                    speak(sentence)

            except json.JSONDecodeError:
                continue

    threading.Thread(target=lambda: summarize_assistant(response_content), daemon=True).start()
    threading.Thread(target=summarize_user, daemon=True).start()


def summarize_assistant(response_content):
    summarize_with_additional(response_content, "assistant")


def summarize_user():
    summarize_with_additional("", "user")


def summarize_with_additional(response_content, role):
    print(f"Summarizing {role}")
    texts = [m["content"] for m in messages if m["role"] == role]
    combined_text = "\n".join(texts + [response_content])

    summary_text = summarize_text(combined_text)

    messages[:] = [m for m in messages if m["role"] != role]
    messages.append({
        "role": role,
        "content": summary_text
    })
    print(f"Summarized {role}")


def summarize_text(previous_content):
    summarization_payload = {
        "model": "deepseek-llm:7b",
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes text concisely and clearly."
            },
            {
                "role": "user",
                "content": f"Summarize the following assistant dialogue:\n\n{previous_content}"
            }
        ]
    }
    summary_resp = requests.post("http://localhost:11434/api/chat", json=summarization_payload)
    summary_text = summary_resp.json()["message"]["content"]
    return summary_text
