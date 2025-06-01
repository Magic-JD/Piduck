import sounddevice as sd
import numpy as np
import scipy.io.wavfile
import tempfile
import time
import whisper
from pathlib import Path
import threading
from collections import deque
from typing import List


class VoiceListener:
    def __init__(self, model_name="base"):
        self.model = whisper.load_model(model_name)
        self.stop_event = threading.Event()
        self.sample_rate = 16000

    def listen(self) -> str:
        from speaker import ensure_queue_empty
        print("Waiting for all previous audio to be executed.")
        ensure_queue_empty()
        print("Ready to record")

        recording = []
        self.stop_event.clear()
        with sd.InputStream(samplerate=self.sample_rate, channels=1,
                            callback=AudioCallback(self.stop_event, self.sample_rate, recording)):
            self.stop_event.wait()

        print("Recording finished")
        return self._process_recording(recording)

    def _process_recording(self, recording: List[np.ndarray]) -> str:
        audio = np.concatenate(recording, axis=0)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            scipy.io.wavfile.write(f.name, self.sample_rate, audio)
            result = self.model.transcribe(f.name)
            Path(f.name).unlink(missing_ok=True)
            return result["text"].strip()


class AudioCallback:
    def __init__(self, stop_event: threading.Event, sample_rate: int, recording: List[np.ndarray]):
        self.silent_duration = 0
        self.max_silent_seconds = 1.5
        self.last_audio_time = time.time()
        self.speaking = False
        self.silence_threshold = 0.01
        self.recording = recording
        self.sample_rate = sample_rate
        block_size = 1024
        self.precording = deque(maxlen=sample_rate // block_size)
        self.stop_event = stop_event

    def __call__(self, indata: np.ndarray, frames, time_info, status) -> None:
        volume_norm = np.linalg.norm(indata) / len(indata)
        now = time.time()
        if volume_norm < self.silence_threshold and self.speaking:
            self.silent_duration += now - self.last_audio_time
        elif volume_norm > self.silence_threshold:
            if not self.speaking:
                self.recording.extend(self.precording)
                print("Recording...")
                self.speaking = True
            self.silent_duration = 0

        if self.speaking:
            self.recording.append(indata.copy())
        else:
            self.precording.append(indata.copy())

        self.last_audio_time = now

        if self.silent_duration >= self.max_silent_seconds:
            self.stop_event.set()
            raise sd.CallbackStop()
