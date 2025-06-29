"""
YAMNet-based cry classifier.
Maps YAMNet class probabilities -> infant cry type.
Handles AUD-01: hunger-cry, pain-cry, discomfort-cry.
"""
import numpy as np
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# Map YAMNet class names -> EdgeWatch cry categories
# These indices correspond to YAMNet label positions
CRY_LABEL_MAP = {
    "Baby cry, infant cry": "hunger_cry",
    "Crying, sobbing":      "discomfort_cry",
    "Screaming":            "pain_cry",
    "Whimpering, dog":      None,   # false positive guard
    "Shout":                None,
}

NON_CRY_LABELS = {
    "Speech", "Music", "Silence", "White noise", "Alarm",
    "Smoke detector, smoke alarm", "Cat",
}

CONFIDENCE_THRESHOLD = 0.40


class CryClassifier:
    def __init__(self, model_path="models/yamnet.tflite"):
        self._model_path = model_path
        self._interp     = None
        self._labels     = []
        self._load()

    def _load(self):
        try:
            import tflite_runtime.interpreter as tflite
            self._interp = tflite.Interpreter(model_path=self._model_path)
            self._interp.allocate_tensors()
            self._in  = self._interp.get_input_details()[0]
            self._out = self._interp.get_output_details()[0]
            logger.info(f"YAMNet loaded from {self._model_path}")
        except Exception as e:
            logger.error(f"Failed to load YAMNet: {e}")
            raise

    def infer(self, audio_float32: np.ndarray) -> dict:
        """
        Run YAMNet inference.
        Returns {cry_type, confidence, raw_top3} or None if no cry detected.
        """
        if self._interp is None:
            return None
        try:
            # YAMNet input: [15360] float32
            inp = audio_float32[:15360].reshape(1, -1).astype(np.float32)
            self._interp.set_tensor(self._in["index"], inp)
            self._interp.invoke()
            scores = self._interp.get_tensor(self._out["index"])[0]  # (521,)

            top_idx   = np.argsort(scores)[::-1][:5]
            top_labels = [(self._labels[i] if self._labels else f"class_{i}",
                           float(scores[i])) for i in top_idx]

            # Check confidence threshold
            best_label, best_score = top_labels[0]
            if best_score < CONFIDENCE_THRESHOLD:
                return None  # not confident enough

            # Map to cry type
            cry_type = CRY_LABEL_MAP.get(best_label)
            if cry_type is None and best_label not in NON_CRY_LABELS:
                cry_type = "unknown_cry"
            if cry_type is None:
                return None  # not a cry event

            return {
                "cry_type":   cry_type,
                "confidence": best_score,
                "top_label":  best_label,
                "top3":       top_labels[:3],
            }
        except Exception as e:
            logger.error(f"YAMNet inference error: {e}")
            return None
