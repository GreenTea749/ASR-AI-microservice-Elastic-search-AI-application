#contains utility functions for the hosted microservice

import librosa

def load_16k(path: str) -> tuple[list[float], int]:
    """
    Loads `path` and resamples to 16 kHz.
    Returns (waveform, sampling_rate)
    """
    waveform, sr = librosa.load(path, sr=16_000)  # librosa will resample
    return waveform, sr
