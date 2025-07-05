"""Extract chest region of interest from MoveNet pose keypoints."""
import numpy as np, cv2, logging

logger = logging.getLogger(__name__)

# Keypoint indices for chest boundary
L_SHOULDER = 5
R_SHOULDER = 6
L_HIP      = 11
R_HIP      = 12
CONF_MIN   = 0.15


def extract_chest_roi(frame: np.ndarray, keypoints: np.ndarray,
                      padding: float = 0.2) -> np.ndarray | None:
    """
    Extract chest region using shoulder + hip keypoints.
    Returns cropped chest frame or None if keypoints insufficient.
    """
    if keypoints is None:
        return None

    kp_indices = [L_SHOULDER, R_SHOULDER, L_HIP, R_HIP]
    pts = keypoints[kp_indices]

    # Check confidence
    if np.mean(pts[:, 2]) < CONF_MIN:
        logger.debug("Chest keypoints too low confidence for ROI")
        return None

    ys, xs = pts[:, 0], pts[:, 1]
    y1, y2 = int(np.min(ys)), int(np.max(ys))
    x1, x2 = int(np.min(xs)), int(np.max(xs))

    # Add padding
    h, w   = frame.shape[:2]
    pad_h  = int((y2 - y1) * padding)
    pad_w  = int((x2 - x1) * padding)
    y1     = max(0, y1 - pad_h)
    y2     = min(h, y2 + pad_h)
    x1     = max(0, x1 - pad_w)
    x2     = min(w, x2 + pad_w)

    if y2 - y1 < 10 or x2 - x1 < 10:
        return None

    chest = frame[y1:y2, x1:x2]
    return cv2.resize(chest, (64, 64))   # fixed size for flow computation
