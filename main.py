from listener import listen_until_keypress
from chat_api import stream_chat

quitwords = ["exit", "quit", "terminate"]

def main():
    while True:
        print("\nTell me all about your problems. Say 'exit' to quit.")
        user_input = listen_until_keypress()
        print(f"You said: {user_input}")
        if user_input.strip().lower() in quitwords:
            break
        if user_input.strip() != "":
            stream_chat(user_input)

if __name__ == "__main__":
    main()
