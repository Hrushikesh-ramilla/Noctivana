"""
Classify infant sleep position from MoveNet keypoints.
VIS-01: detect prone (face-down) and trigger CRITICAL alert.
Positions: supine (back), prone (face-down), side.
"""
import numpy as np, logging, time, collections

logger = logging.getLogger(__name__)

# Confidence thresholds
FACE_KP_INDICES = [0, 1, 2, 3, 4]   # nose, eyes, ears
BACK_KP_INDICES = [5, 6, 11, 12]    # shoulders, hips
CONF_LOW        = 0.15
PRONE_CONF      = 0.25              # from config, conservative per SRS


class PoseClassifier:
    def __init__(self, prone_conf=PRONE_CONF, side_window_s=3.0):
        self._prone_conf    = prone_conf
        self._history       = collections.deque(maxlen=30)  # ~6s at 5fps
        self._prone_since   = None

    def classify(self, keypoints: np.ndarray) -> dict:
        """
        Returns {position, confidence, prone_sustained_s}
        position: 'supine' | 'prone' | 'side' | 'unknown'
        """
        if keypoints is None:
            return {"position": "unknown", "confidence": 0.0, "prone_sustained_s": 0}

        face_conf   = float(np.mean(keypoints[FACE_KP_INDICES, 2]))
        back_conf   = float(np.mean(keypoints[BACK_KP_INDICES, 2]))
        nose_conf   = float(keypoints[0, 2])  # nose
        all_conf    = float(np.mean(keypoints[:, 2]))

        # Supine: face visible, back keypoints high confidence
        if face_conf > 0.4 and back_conf > 0.3:
            position   = "supine"
            confidence = face_conf
            self._prone_since = None

        # Prone: face keypoints very low, some body visible
        elif face_conf < self._prone_conf and back_conf > 0.2:
            position   = "prone"
            confidence = 1.0 - face_conf  # inverse: higher when face more hidden
            now = time.time()
            if self._prone_since is None:
                self._prone_since = now
        else:
            # Side: intermediate - use shoulder/hip angle
            position   = "side"
            confidence = all_conf
            self._prone_since = None

        prone_sustained = 0.0
        if self._prone_since and position == "prone":
            prone_sustained = time.time() - self._prone_since

        self._history.append(position)
        return {
            "position":          position,
            "confidence":        round(confidence, 3),
            "face_conf":         round(face_conf, 3),
            "back_conf":         round(back_conf, 3),
            "prone_sustained_s": round(prone_sustained, 1),
        }

    def is_prone_alert(self, result: dict) -> bool:
        """True if prone sustained long enough to trigger CRITICAL alert."""
        return (result["position"] == "prone" and
                result["prone_sustained_s"] >= 5.0)   # 5s per VIS-01
