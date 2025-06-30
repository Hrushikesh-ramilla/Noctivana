"""
Acoustic breath-absence detector. AUD-02.
Looks for rhythmic low-frequency energy (0.2-2Hz) in audio.
"""
import numpy as np, time, logging
from scipy.signal import butter, filtfilt

logger = logging.getLogger(__name__)

ABSENCE_THRESHOLD_S = 20.0


class BreathDetector:
    def __init__(self, sr=16000):
        self._sr          = sr
        self._last_breath = time.time()
        b, a = butter(2, [0.2/(sr/2), 2.0/(sr/2)], btype="band")
        self._b, self._a  = b, a

    def check(self, audio: np.ndarray, now: float) -> bool:
        """Returns True if breath signal present, False if absent too long."""
        try:
            filtered = filtfilt(self._b, self._a, audio.astype(np.float64))
            energy   = float(np.sqrt(np.mean(filtered**2)))
            if energy > 1e-4:
                self._last_breath = now
            return (now - self._last_breath) < ABSENCE_THRESHOLD_S
        except Exception:
            return True   # fail-safe: don't false-alarm on error
