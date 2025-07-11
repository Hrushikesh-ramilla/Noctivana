"""
rPPG (remote photoplethysmography) heart rate estimator.
VIT-04: EXPERIMENTAL - pulse from green channel skin variation.
NOTE: Accuracy is very low at ceiling distance. Included as proof-of-concept.
"""
import numpy as np, cv2, logging, collections
from scipy.signal import butter, filtfilt

logger = logging.getLogger(__name__)

HR_MIN_HZ = 0.8   # 48 bpm
HR_MAX_HZ = 3.0   # 180 bpm
WINDOW_S  = 10.0
FPS       = 5


class RPPGEstimator:
    def __init__(self, fps=FPS):
        self._fps     = fps
        self._history = collections.deque(maxlen=int(WINDOW_S * fps))
        self._face_pos = None
        b, a = butter(2, [HR_MIN_HZ/(fps/2), HR_MAX_HZ/(fps/2)], btype="band")
        self._b, self._a = b, a

    def estimate(self, frame: np.ndarray) -> dict | None:
        """
        Estimate heart rate from green channel mean in face region.
        Returns {"bpm": float, "confidence": float, "experimental": True} or None.
        """
        try:
            # Use center-upper region as rough face proxy at ceiling distance
            h, w = frame.shape[:2]
            face_roi = frame[h//6:h//2, w//3:2*w//3]
            if face_roi.size == 0:
                return None

            g_mean = float(np.mean(face_roi[:,:,1]))   # green channel mean
            self._history.append(g_mean)

            if len(self._history) < int(WINDOW_S * self._fps * 0.5):
                return None

            signal_arr = np.array(self._history)
            # Detrend
            signal_arr -= np.mean(signal_arr)
            # Filter
            try:
                filtered = filtfilt(self._b, self._a, signal_arr.astype(np.float64))
            except Exception:
                return None

            fft_mag = np.abs(np.fft.rfft(filtered))
            freqs   = np.fft.rfftfreq(len(filtered), d=1.0/self._fps)
            mask    = (freqs >= HR_MIN_HZ) & (freqs <= HR_MAX_HZ)
            if not mask.any():
                return None

            dom_freq   = float(freqs[mask][np.argmax(fft_mag[mask])])
            bpm        = dom_freq * 60.0
            confidence = min(0.5, float(np.max(fft_mag[mask])) / (np.mean(fft_mag)+1e-6))
            # Cap confidence at 0.5 - this method is inherently unreliable
            return {"bpm": round(bpm, 1), "confidence": round(confidence, 3), "experimental": True}
        except Exception as e:
            logger.debug(f"rPPG error: {e}")
            return None
