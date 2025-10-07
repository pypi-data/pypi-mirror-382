import os
from threading import Thread
import time
import wave
import numpy as np
import simpleaudio as sa  # type: ignore
from .generate_wav import generate_wav


def _play_wav(filepath: str, vol: float) -> None:
    with wave.open(filepath, "rb") as wf:
        data = wf.readframes(wf.getnframes())
        audio = np.frombuffer(data, dtype=np.int16)
        audio = (audio * vol).astype(np.int16)
        sa.play_buffer(audio, wf.getnchannels(), wf.getsampwidth(), wf.getframerate())  # type: ignore

    time.sleep(len(audio) / wf.getframerate() / wf.getnchannels())


def beep(vol: float = 1.0, blocking: bool = False) -> None:
    """Plays an alert sound. Always plays the sound till completion before allowing the program to exit.

    Args:
        vol (float): The playback volume, must be from interval [0.0, 1.0]
        blocking (Optional, bool): If true, the function call is blocking
    """
    vol = max(0.0, min(1.0, vol))
    filepath = os.path.join(os.path.dirname(__file__), ".data", "beep.wav")
    if os.path.exists(filepath):
        pass
    else:
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
        generate_wav(filepath)

    if not blocking:
        t = Thread(target=_play_wav, args=(filepath, vol), daemon=False)
        t.start()
    else:
        _play_wav(filepath, vol)
