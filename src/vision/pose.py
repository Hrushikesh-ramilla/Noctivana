"""
MoveNet pose estimation wrapper.
Extracts 17 body keypoints from camera frames.
"""
import numpy as np, logging, time

logger = logging.getLogger(__name__)

KEYPOINT_NAMES = [
    "nose","left_eye","right_eye","left_ear","right_ear",
    "left_shoulder","right_shoulder","left_elbow","right_elbow",
    "left_wrist","right_wrist","left_hip","right_hip",
    "left_knee","right_knee","left_ankle","right_ankle"
]


class PoseEstimator:
    def __init__(self, model_path="models/movenet_lightning.tflite"):
        self._path  = model_path
        self._interp = None
        self._in     = None
        self._out    = None
        self._load()

    def _load(self):
        try:
            import tflite_runtime.interpreter as tflite
            self._interp = tflite.Interpreter(model_path=self._path)
            self._interp.allocate_tensors()
            self._in  = self._interp.get_input_details()[0]
            self._out = self._interp.get_output_details()[0]
            logger.info(f"MoveNet loaded: {self._path}")
        except Exception as e:
            logger.error(f"MoveNet load failed: {e}")
            raise

    def infer(self, frame_bgr: np.ndarray) -> np.ndarray | None:
        """
        Run MoveNet inference on a BGR frame (192x192 expected after ROI upscale).
        Returns keypoints array (17, 3): [y_px, x_px, confidence] or None.
        """
        if self._interp is None:
            return None
        try:
            import cv2
            inp = cv2.resize(frame_bgr, (192, 192))
            inp = inp.astype(np.uint8)[np.newaxis]   # (1, 192, 192, 3)
            self._interp.set_tensor(self._in["index"], inp)
            self._interp.invoke()
            raw = self._interp.get_tensor(self._out["index"])  # (1,1,17,3)
            kpts = raw[0, 0]   # (17, 3): [y_norm, x_norm, conf]
            # Scale to 192x192 pixel coords
            kpts_px = kpts.copy()
            kpts_px[:, 0] *= 192
            kpts_px[:, 1] *= 192
            return kpts_px
        except Exception as e:
            logger.error(f"MoveNet inference error: {e}")
            return None

    def keypoint(self, kpts: np.ndarray, name: str) -> tuple:
        """Get (y, x, confidence) for a named keypoint."""
        idx = KEYPOINT_NAMES.index(name)
        return tuple(kpts[idx])
