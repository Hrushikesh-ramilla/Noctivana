#!/usr/bin/env python3
"""Raspberry Pi camera hardware abstraction via picamera2."""
import time, logging
import numpy as np

logger = logging.getLogger(__name__)


class Camera:
    """picamera2 wrapper for EdgeWatch vision pipeline."""

    def __init__(self, resolution=(640, 480), fps=5):
        self.resolution = resolution
        self.fps = fps
        self._picam = None
        self._is_night_mode = False

    def start(self):
        from picamera2 import Picamera2
        self._picam = Picamera2()
        cfg = self._picam.create_video_configuration(
            main={"size": self.resolution, "format": "BGR888"}
        )
        self._picam.configure(cfg)
        self._picam.set_controls({"FrameRate": self.fps})
        self._picam.start()
        time.sleep(0.5)
        logger.info(f"Camera started {self.resolution}@{self.fps}fps")

    def capture_frame(self):
        """Returns numpy BGR frame or None on failure."""
        if self._picam is None:
            return None
        try:
            frame = self._picam.capture_array()
            if frame is None or frame.size == 0:
                logger.warning("Empty frame returned")
                return None
            return frame
        except Exception as e:
            logger.warning(f"Frame capture error: {e}")
            return None

    def set_night_mode(self, enabled: bool):
        """Switch between auto and manual IR exposure."""
        if self._picam is None:
            return
        if enabled and not self._is_night_mode:
            self._picam.set_controls({
                "AeEnable": False,
                "ExposureTime": 33333,
                "AnalogueGain": 4.0,
                "Brightness": -0.1,
            })
            self._is_night_mode = True
            logger.info("Night mode ON")
        elif not enabled and self._is_night_mode:
            self._picam.set_controls({"AeEnable": True})
            self._is_night_mode = False
            logger.info("Night mode OFF")

    def set_fps(self, fps: int):
        self.fps = fps
        if self._picam:
            self._picam.set_controls({"FrameRate": fps})

    def stop(self):
        if self._picam:
            self._picam.stop()
            self._picam = None

    def __del__(self):
        self.stop()
