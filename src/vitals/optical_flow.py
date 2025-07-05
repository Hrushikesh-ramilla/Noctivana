"""
Optical flow respiratory rate estimation.
VIT-01: estimate breaths/min from chest-rise motion.
Uses Farneback dense optical flow on chest ROI.
"""
import cv2, numpy as np, logging, collections
from scipy.signal import butter, filtfilt, find_peaks

logger = logging.getLogger(__name__)

# Best params after tuning Aug 8
FB_PARAMS = dict(
    pyr_scale=0.5, levels=3, winsize=21,
    iterations=3, poly_n=7, poly_sigma=1.5, flags=0
)
BANDPASS_LOW  = 0.15   # Hz (9 bpm)
BANDPASS_HIGH = 1.0    # Hz (60 bpm)
WINDOW_S      = 45.0   # seconds for FFT window
FPS           = 5


class OpticalFlowBreathing:
    def __init__(self, fps=FPS, sr_hz=None):
        self.fps      = fps
        self._history = collections.deque(maxlen=int(WINDOW_S * fps))
        self._prev    = None
        b, a = butter(2, [BANDPASS_LOW/(fps/2), BANDPASS_HIGH/(fps/2)], btype="band")
        self._b, self._a = b, a
        self._ema_bpm = None

    def update(self, chest_roi: np.ndarray) -> dict:
        """
        Process one chest crop frame. Returns current resp rate estimate.
        """
        gray = cv2.cvtColor(chest_roi, cv2.COLOR_BGR2GRAY) if len(chest_roi.shape)==3 else chest_roi

        if self._prev is None:
            self._prev = gray
            return {"bpm": None, "confidence": 0.0, "method": "optical_flow"}

        try:
            flow = cv2.calcOpticalFlowFarneback(self._prev, gray, None, **FB_PARAMS)
            # Vertical flow magnitude = primary chest-rise signal
            vy_mean = float(np.mean(np.abs(flow[..., 1])))
            self._history.append(vy_mean)
            self._prev = gray

            if len(self._history) < int(WINDOW_S * self.fps * 0.5):
                return {"bpm": None, "confidence": 0.0, "method": "optical_flow"}

            # FFT-based frequency estimation
            signal_arr = np.array(self._history)
            try:
                filtered = filtfilt(self._b, self._a, signal_arr.astype(np.float64))
            except Exception:
                filtered = signal_arr

            fft_mag = np.abs(np.fft.rfft(filtered))
            freqs   = np.fft.rfftfreq(len(filtered), d=1.0/self.fps)
            mask    = (freqs >= BANDPASS_LOW) & (freqs <= BANDPASS_HIGH)
            if not mask.any():
                return {"bpm": None, "confidence": 0.0, "method": "optical_flow"}

            dom_freq = float(freqs[mask][np.argmax(fft_mag[mask])])
            bpm_raw  = dom_freq * 60.0

            # Exponential moving average for stability
            alpha = 0.3
            if self._ema_bpm is None:
                self._ema_bpm = bpm_raw
            else:
                self._ema_bpm = alpha * bpm_raw + (1 - alpha) * self._ema_bpm

            confidence = min(1.0, float(np.max(fft_mag[mask])) / (np.mean(fft_mag) + 1e-6))
            return {
                "bpm":        round(self._ema_bpm, 1),
                "confidence": round(min(confidence, 1.0), 3),
                "method":     "optical_flow",
            }
        except Exception as e:
            logger.warning(f"Optical flow error: {e}")
            return {"bpm": None, "confidence": 0.0, "method": "optical_flow"}
