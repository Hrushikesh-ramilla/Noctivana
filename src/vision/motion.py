"""
Infant motion level tracker.
VIS-04: classify still/low-movement/restless over 30-sec windows.
"""
import cv2, numpy as np, logging, collections, time

logger = logging.getLogger(__name__)

WINDOW_S = 30.0
FPS      = 5


class MotionTracker:
    def __init__(self, fps=FPS):
        self._fps     = fps
        self._history = collections.deque(maxlen=int(WINDOW_S * fps))

    def update(self, frame: np.ndarray, prev_frame: np.ndarray) -> dict:
        """
        Compare current vs previous frame.
        Returns motion level: still | low | restless.
        """
        try:
            gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            diff  = cv2.absdiff(gray1, gray2)
            _, th = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
            changed_pct = float(np.sum(th > 0)) / th.size

            self._history.append(changed_pct)
            avg = float(np.mean(self._history))

            if avg < 0.02:
                level = "still"
            elif avg < 0.08:
                level = "low"
            else:
                level = "restless"

            return {
                "level":       level,
                "changed_pct": round(changed_pct, 4),
                "window_avg":  round(avg, 4),
                "ts":          time.time(),
            }
        except Exception as e:
            logger.warning(f"Motion tracker error: {e}")
            return {"level": "unknown", "changed_pct": 0.0, "window_avg": 0.0}
