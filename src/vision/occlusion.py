"""
Face occlusion detector.
VIS-02: alert when >40% face region covered for >3 seconds.
"""
import numpy as np, time, logging, collections

logger = logging.getLogger(__name__)

# Face keypoint indices
FACE_KP = [0, 1, 2, 3, 4]   # nose, l_eye, r_eye, l_ear, r_ear
BODY_KP = [5, 6, 11, 12]    # shoulders, hips (body still visible)


class OcclusionDetector:
    def __init__(self, coverage_thr=0.40, duration_s=3.0):
        self._cov_thr    = coverage_thr
        self._dur        = duration_s
        self._occ_since  = None
        self._conf_hist  = collections.deque(maxlen=20)  # ~4s at 5fps

    def check(self, keypoints: np.ndarray, now: float,
               night_mode: bool = False) -> dict:
        """
        Estimate face occlusion from keypoint confidence dropout.
        Different algorithm for day vs IR mode.
        """
        if keypoints is None:
            return {"occluded": False, "coverage_pct": 0.0, "sustained_s": 0.0}

        face_confs = keypoints[FACE_KP, 2]
        body_confs = keypoints[BODY_KP, 2]
        face_mean  = float(np.mean(face_confs))
        body_mean  = float(np.mean(body_confs))

        if night_mode:
            # IR algorithm: stricter (all face kp must drop) + body visible
            occluded = (np.all(face_confs < 0.1) and body_mean > 0.15)
        else:
            # Daytime: coverage based on proportion of low-confidence face kp
            n_low    = int(np.sum(face_confs < 0.2))
            cov_pct  = n_low / len(FACE_KP)
            # Head turn guard: if body also invisible, it's just head turn
            head_turn = body_mean < 0.1
            occluded  = (cov_pct >= self._cov_thr) and not head_turn

        # Temporal filter (VIS-02: >3s sustained)
        if occluded:
            if self._occ_since is None:
                self._occ_since = now
            sustained = now - self._occ_since
        else:
            self._occ_since = None
            sustained = 0.0

        is_alert = (occluded and sustained >= self._dur)

        return {
            "occluded":     is_alert,
            "raw_occluded": occluded,
            "face_conf":    round(face_mean, 3),
            "body_conf":    round(body_mean, 3),
            "sustained_s":  round(sustained, 1),
            "coverage_pct": round(face_mean, 3),   # approx
        }
