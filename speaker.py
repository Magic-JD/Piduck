from queue import Queue
from TTS.api import TTS
import tempfile
import threading
import simpleaudio as sa
import os

tts_engine = TTS(model_name="tts_models/en/ljspeech/vits", progress_bar=False, gpu=False)

audio_queue = Queue()


def ensure_queue_empty():
    audio_queue.join()


def playback_worker():
    while True:
        file_path = audio_queue.get()
        if file_path is None:  # Sentinel value to stop thread
            break
        try:
            wave_obj = sa.WaveObject.from_wave_file(file_path)
            play_obj = wave_obj.play()
            play_obj.wait_done()
        finally:
            os.unlink(file_path)  # Clean up
            audio_queue.task_done()

# Start the playback thread
threading.Thread(target=playback_worker, daemon=True).start()

# Main interface to queue up speech
def speak(text):
    def tts_worker():
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tts_engine.tts_to_file(text=text, file_path=f.name)
            audio_queue.put(f.name)

    threading.Thread(target=tts_worker, daemon=True).start()
