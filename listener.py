import sounddevice as sd
import numpy as np
import scipy.io.wavfile
import tempfile
import time
import whisper
import os
import threading
from speaker import ensure_queue_empty
from chat_api import buffer_completed
from collections import deque

SAMPLE_RATE = 16000
BLOCK_SIZE = 1024

SECOND_SIZE = SAMPLE_RATE // BLOCK_SIZE


whisper_model = whisper.load_model("base")
stop_event = threading.Event()

SILENCE_THRESHOLD = 0.01
MAX_SILENT_SECONDS = 1.5

def listen_until_keypress():
    print("Waiting for all previous audio to be executed.")
    buffer_completed()
    ensure_queue_empty()
    print("Ready to record")

    recording = []
    precording = deque(maxlen=SECOND_SIZE)

    silent_duration = 0
    speaking = False
    last_audio_time = time.time()

    def callback(indata, frames, time_info, status):
        nonlocal silent_duration, last_audio_time, speaking
        volume_norm = np.linalg.norm(indata) / len(indata)
        ensure_queue_empty()
        now = time.time()
        if volume_norm < SILENCE_THRESHOLD and speaking:
            silent_duration += now - last_audio_time
        elif volume_norm > SILENCE_THRESHOLD:
            if not speaking:
                recording.extend(precording)
                print("Recording...")
                speaking = True
            silent_duration = 0

        if speaking:
            recording.append(indata.copy())
        else:
            precording.append(indata.copy())

        last_audio_time = now

        if silent_duration >= MAX_SILENT_SECONDS:
            stop_event.set()
            raise sd.CallbackStop()

    stop_event.clear()

    stream = sd.InputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, channels=1, callback=callback)
    with stream:
        stop_event.wait()

    print("Recording finished")

    audio = np.concatenate(recording, axis=0)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        scipy.io.wavfile.write(f.name, SAMPLE_RATE, audio)
        result = whisper_model.transcribe(f.name)
        os.unlink(f.name)
        return result["text"].strip()
