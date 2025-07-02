"""
Crib region-of-interest (ROI) management.
Stores calibrated crib bounding box (pixels) in config.
VIS-06: auto-recalibration triggered from parent app.
"""
import json, logging, os
import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_ROI = [0, 0, 640, 480]   # full frame fallback


class CribROI:
    def __init__(self, config_path="config/config.yaml"):
        self._roi  = DEFAULT_ROI  # [x1, y1, x2, y2]
        self._load(config_path)

    def _load(self, config_path):
        try:
            import yaml
            with open(config_path) as f:
                cfg = yaml.safe_load(f)
            roi = cfg.get("crib_roi")
            if roi and len(roi) == 4:
                self._roi = roi
                logger.info(f"Loaded crib ROI: {roi}")
            else:
                logger.warning("No calibrated ROI in config, using full frame")
        except Exception as e:
            logger.warning(f"ROI load failed: {e}, using full frame")

    def crop(self, frame: np.ndarray) -> tuple:
        """
        Crop frame to crib ROI.
        Returns (cropped_frame, offset_xy) for coordinate remapping.
        """
        x1, y1, x2, y2 = self._roi
        x1 = max(0, x1); y1 = max(0, y1)
        x2 = min(frame.shape[1], x2)
        y2 = min(frame.shape[0], y2)
        cropped = frame[y1:y2, x1:x2]
        return cropped, (x1, y1)

    def upscale_for_inference(self, crop: np.ndarray, target=256) -> np.ndarray:
        """
        Upscale crib crop to target size using INTER_LINEAR.
        Better keypoint confidence from ceiling distance.
        """
        import cv2
        return cv2.resize(crop, (target, target), interpolation=cv2.INTER_LINEAR)

    def remap_keypoints(self, keypoints: np.ndarray,
                        offset_xy: tuple, crop_shape: tuple,
                        inf_size: int = 256) -> np.ndarray:
        """Map keypoint coords from inference space back to full-frame pixels."""
        ox, oy     = offset_xy
        ch, cw     = crop_shape[:2]
        scale_x    = cw / inf_size
        scale_y    = ch / inf_size
        remapped   = keypoints.copy()
        # keypoints: (17, 3) -> [y_norm, x_norm, confidence]
        remapped[:, 0] = keypoints[:, 0] * inf_size * scale_y + oy
        remapped[:, 1] = keypoints[:, 1] * inf_size * scale_x + ox
        return remapped

    @property
    def roi(self):
        return self._roi
