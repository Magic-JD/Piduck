# 🐥 Piduck

Piduck is a voice-activated, locally running rubber duck debugging assistant. It allows you to talk through your programming challenges out loud and receive thoughtful, Socratic questions from a language model in response — all using your voice.

## Purpose

Piduck is designed to help developers think more clearly about their work by externalizing thoughts and receiving non-directive, guiding questions in return — a core principle of rubber duck debugging.

## How It Works

- You speak your thoughts aloud.

- Piduck listens, transcribes, and sends your message to a local LLM.

- The LLM, acting as “Duck”, responds with structured, open-ended questions.

- Piduck reads the response back to you using text-to-speech.

This creates a natural, reflective debugging process — entirely via voice.

## Features

    Fully voice-driven interaction.

    Strictly Socratic responses from the LLM (no direct answers or advice).

    Local LLM querying via Ollama (required).

    Configurable model backend (tested with DeepSeek).

    Prototype implementation with modular structure for extension.

## Requirements

    Python 3.10+

    A running instance of Ollama on localhost:11434.
