from typing import List
import wave
import numpy as np


def generate_wav(filepath: str) -> None:
    """Generates and audio file for future playback."""
    notes = [
        (440.0, 0.2),
        (554.365, 0.2),
        (659.255, 0.2),
        (880.0, 0.2),
        (0.0, 0.2),
        (659.255, 0.2),
        (880.0, 0.8),
    ]

    sample_rate = 44100
    amplitude = 32767

    samples: List[float] = []

    for freq, duration in notes:
        duration *= 1.2
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)
        wave_data = np.sin(2 * np.pi * freq * t)
        samples.extend(wave_data.tolist())

    samples_int16 = np.int16(np.array(samples) * amplitude)

    # Write all frames at once (much better)
    with wave.open(filepath, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples_int16.tobytes())
