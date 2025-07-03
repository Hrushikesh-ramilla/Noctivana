#!/usr/bin/env python3
"""
Vision monitoring service.
Camera -> MoveNet -> pose/occlusion/motion -> ZMQ publish.
Covers: VIS-01 (prone), VIS-02 (occlusion), VIS-03 (IR mode),
        VIS-04 (motion tracking), VIS-05 (no storage), VIS-06 (ROI calibration).
"""
import time, signal, sys, os, logging, gc
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.hardware.camera       import Camera
from src.hardware.ir_led       import IRLed
from src.hardware.status_led   import StatusLED
from src.hardware.sensors      import BH1750
from src.vision.roi            import CribROI
from src.vision.pose           import PoseEstimator
from src.vision.pose_classifier import PoseClassifier
from src.vision.occlusion      import OcclusionDetector
from src.vision.motion         import MotionTracker
from src.vision.night_mode     import NightModeController
from src.utils.zmq_bus         import Publisher
from src.utils.config_loader   import get_config
from src.utils.logger          import setup_logger
import smbus2

logger = setup_logger("vision_service")


class VisionService:
    def __init__(self, cfg_path="config/config.yaml"):
        self.cfg        = get_config(cfg_path)
        fps             = self.cfg.get("hardware","camera_fps",default=5)
        res             = self.cfg.get("hardware","camera_resolution",default=[640,480])
        self.camera     = Camera(resolution=tuple(res), fps=fps)
        self.ir_led     = IRLed(pin=self.cfg.get("hardware","ir_led_pin",default=17))
        self.roi        = CribROI(cfg_path)
        self.pose_est   = PoseEstimator(
            model_path=self.cfg.get("paths","models_dir","models")+"/movenet_lightning.tflite")
        self.classifier = PoseClassifier(
            prone_conf=self.cfg.get("thresholds","prone_confidence",default=0.25))
        self.occlusion  = OcclusionDetector(
            coverage_thr=self.cfg.get("thresholds","occlusion_coverage_pct",default=0.4),
            duration_s=self.cfg.get("thresholds","occlusion_duration_s",default=3.0))
        self.motion     = MotionTracker()
        self.night_ctrl = NightModeController(
            lux_threshold=self.cfg.get("thresholds","lux_ir_threshold",default=5.0))
        self.pub        = Publisher()
        self._run       = True
        self._frame_n   = 0
        self._low_power = False
        self._fps_target = fps
        signal.signal(signal.SIGTERM, self._stop)
        signal.signal(signal.SIGINT,  self._stop)

    def _stop(self, *_):
        self._run = False

    def _enter_low_power(self):
        if not self._low_power:
            self._low_power = True
            self.camera.set_fps(2)
            logger.info("Entered low-power mode (2fps)")

    def _exit_low_power(self):
        if self._low_power:
            self._low_power = False
            self.camera.set_fps(self._fps_target)
            logger.info("Exited low-power mode")

    def run(self):
        logger.info("vision_service starting...")
        self.ir_led.setup()
        self.camera.start()
        prev_frame = None
        still_since = None

        while self._run:
            try:
                frame = self.camera.capture_frame()

                # Frame safety checks (NFR-R3 related, thermal dropped frames)
                if frame is None:
                    logger.warning("Null frame skipped")
                    time.sleep(0.1); continue
                if frame.size == 0:
                    logger.warning("Empty frame skipped")
                    time.sleep(0.1); continue

                self._frame_n += 1
                now = time.time()

                # Night mode control (VIS-03)
                night_on = self.night_ctrl.should_enable()
                self.camera.set_night_mode(night_on)
                self.ir_led.enable() if night_on else self.ir_led.disable()

                # Apply CLAHE in IR mode for better contrast
                import cv2
                if night_on:
                    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
                    gray  = clahe.apply(gray)
                    frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

                # Crop + upscale ROI for better inference from ceiling distance
                crop, offset = self.roi.crop(frame)
                if crop.size == 0:
                    time.sleep(0.05); continue
                upscaled = self.roi.upscale_for_inference(crop, target=256)

                # Pose estimation
                kpts = self.pose_est.infer(upscaled)
                pose = self.classifier.classify(kpts)
                self.pub.send("vision/pose", pose)

                # Face occlusion check (VIS-02) - every frame (safety critical)
                occ = self.occlusion.check(kpts, now, night_mode=night_on)
                self.pub.send("vision/occlusion", occ)

                # Motion tracking (VIS-04) - alternate frames to save CPU
                if self._frame_n % 2 == 0 and prev_frame is not None:
                    motion = self.motion.update(crop, prev_frame)
                    self.pub.send("vision/motion", motion)
                    # Low-power mode management (NFR-P4)
                    if motion["level"] == "still":
                        if still_since is None:
                            still_since = now
                        elif now - still_since >= 300:  # 5min still
                            self._enter_low_power()
                    else:
                        still_since = None
                        self._exit_low_power()

                prev_frame = crop.copy()

                # Periodic GC to prevent memory accumulation
                if self._frame_n % 100 == 0:
                    del frame, crop, upscaled
                    gc.collect()

                time.sleep(max(0, 1.0/self._fps_target - 0.05))

            except Exception as e:
                logger.error(f"vision_service frame error: {e}", exc_info=True)
                time.sleep(0.5)

        self.camera.stop()
        self.ir_led.cleanup()
        logger.info("vision_service stopped")


if __name__ == "__main__":
    VisionService().run()
