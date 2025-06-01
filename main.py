from listener import VoiceListener
from chat_api import stream_chat


def main() -> None:
    voice_listener = VoiceListener()
    quitwords = {"exit", "quit", "terminate"}
    while True:
        print("\nTell me all about your problems. Say 'exit' to quit.")
        user_input = voice_listener.listen()
        print(f"You said: {user_input}")
        if user_input.strip().lower() in quitwords:
            break
        if user_input:
            stream_chat(user_input)


if __name__ == "__main__":
    main()
