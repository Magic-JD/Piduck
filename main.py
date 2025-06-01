from listener import VoiceListener
from chat_api import ChatStreamer
from speaker import Speaker


def main() -> None:
    speaker = Speaker()
    voice_listener = VoiceListener(speaker)
    chat_streamer = ChatStreamer(speaker_instance=speaker)
    quitwords = {"exit", "quit", "terminate"}
    while True:
        print("\nTell me all about your problems. Say 'exit' to quit.")
        user_input = voice_listener.listen()
        print(f"You said: {user_input}")
        if user_input.strip().lower() in quitwords:
            break
        if user_input:
            chat_streamer.stream_chat(user_input)


if __name__ == "__main__":
    main()
