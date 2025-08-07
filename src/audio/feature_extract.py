"""Audio feature extraction pipeline: raw audio -> mel spectrogram / MFCC."""
import numpy as np
import logging

logger = logging.getLogger(__name__)

try:
    import librosa
    LIBROSA_OK = True
except ImportError:
    LIBROSA_OK = False
    logger.warning("librosa not available, using numpy fallback")

SR = 16000   # sample rate


def compute_yamnet_input(audio_float32: np.ndarray, target_sr=SR) -> np.ndarray:
    """
    Prepare audio for YAMNet TFLite inference.
    YAMNet expects: float32, normalized [-1, 1], 16kHz mono, 0.96s windows.
    """
    # Ensure float32 normalized
    if audio_float32.dtype != np.float32:
        audio_float32 = audio_float32.astype(np.float32)
    # Clip to [-1, 1]
    audio_float32 = np.clip(audio_float32, -1.0, 1.0)
    # Pad or trim to exactly 15360 samples (0.96s @ 16kHz)
    target_len = int(0.96 * SR)
    if len(audio_float32) < target_len:
        audio_float32 = np.pad(audio_float32, (0, target_len - len(audio_float32)))
    else:
        audio_float32 = audio_float32[:target_len]
    return audio_float32


def compute_mfcc(audio_float32: np.ndarray, n_mfcc=40, sr=SR) -> np.ndarray:
    """Compute MFCC features (fallback / supplementary)."""
    if LIBROSA_OK:
        mfcc = librosa.feature.mfcc(y=audio_float32, sr=sr, n_mfcc=n_mfcc)
        return mfcc.T  # (time, n_mfcc)
    # Numpy fallback
    logger.warning("Using numpy MFCC fallback (librosa not available)")
    return np.zeros((40, n_mfcc), dtype=np.float32)


def rms_to_db(audio_float32: np.ndarray) -> float:
    """Compute RMS energy in dB SPL."""
    rms = np.sqrt(np.mean(audio_float32 ** 2))
    return float(20 * np.log10(rms + 1e-9))
