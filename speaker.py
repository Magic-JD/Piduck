import simpleaudio as sa
import tempfile
import threading
from TTS.api import TTS
from pathlib import Path
from queue import Queue


class Speaker:
    def __init__(self, model_name="tts_models/en/ljspeech/vits", gpu=False):
        self.tts_engine = TTS(model_name=model_name, progress_bar=False, gpu=gpu)
        self.text_queue = Queue()
        self.audio_queue = Queue()
        self._stop_event = threading.Event()

        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.playback_thread = threading.Thread(target=self._playback_worker, daemon=True)

        self.tts_thread.start()
        self.playback_thread.start()

    def _tts_worker(self):
        while not self._stop_event.is_set():
            text = self.text_queue.get()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                self.tts_engine.tts_to_file(text=text, file_path=f.name)
                self.audio_queue.put(f.name)
            self.text_queue.task_done()

    def _playback_worker(self):
        while not self._stop_event.is_set():
            file_path = self.audio_queue.get()
            try:
                wave_obj = sa.WaveObject.from_wave_file(file_path)
                play_obj = wave_obj.play()
                play_obj.wait_done()
            finally:
                Path(file_path).unlink(missing_ok=True)
                self.audio_queue.task_done()

    def speak(self, text: str):
        if self._stop_event.is_set():
            print("Warning: Speaker is shut down. Cannot queue new text.")
            return
        self.text_queue.put(text)

    def ensure_queue_empty(self):
        self.text_queue.join()
        self.audio_queue.join()
