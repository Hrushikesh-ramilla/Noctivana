#!/usr/bin/env python3
"""
Vital signs monitoring service.
Optical flow respiratory rate + experimental rPPG.
Covers: VIT-01, VIT-03, VIT-04, VIT-05.
"""
import time, signal, sys, os, logging, collections
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.hardware.camera   import Camera
from src.vitals.optical_flow import OpticalFlowBreathing
from src.vitals.chest_roi  import extract_chest_roi
from src.vitals.rppg       import RPPGEstimator
from src.vision.roi        import CribROI
from src.utils.zmq_bus     import Publisher, Subscriber
from src.utils.config_loader import get_config
from src.utils.logger      import setup_logger

logger = setup_logger("vitals_service")

RESP_ABSENCE_THRESHOLD_S = 15.0


class VitalsService:
    def __init__(self, cfg_path="config/config.yaml"):
        self.cfg        = get_config(cfg_path)
        self.camera     = Camera(
            resolution=tuple(self.cfg.get("hardware","camera_resolution",default=[640,480])),
            fps=self.cfg.get("hardware","camera_fps",default=5))
        self.roi        = CribROI(cfg_path)
        self.of_breath  = OpticalFlowBreathing(fps=5)
        self.rppg       = RPPGEstimator()
        self.pub        = Publisher()
        self.pose_sub   = Subscriber(["vision/pose"])
        self._run       = True
        self._latest_kpts = None
        self._last_resp_t = time.time()
        self._frame_n   = 0
        signal.signal(signal.SIGTERM, self._stop)
        signal.signal(signal.SIGINT,  self._stop)

    def _stop(self, *_):
        self._run = False

    def _update_pose(self):
        msg = self.pose_sub.recv(timeout_ms=10)
        if msg and msg.get("data"):
            self._latest_kpts = msg["data"].get("keypoints")

    def run(self):
        logger.info("vitals_service starting...")
        self.camera.start()

        while self._run:
            try:
                self._update_pose()
                frame = self.camera.capture_frame()
                if frame is None:
                    time.sleep(0.1); continue

                self._frame_n += 1
                now = time.time()

                crop, _ = self.roi.crop(frame)

                # Optical flow respiratory rate (VIT-01)
                chest = extract_chest_roi(crop, None)  # full chest fallback
                if chest is None:
                    chest = crop
                resp = self.of_breath.update(chest)
                self.pub.send("vitals/resp", resp)

                # Respiratory absence check (VIT-03)
                if resp.get("bpm") and resp["bpm"] > 0:
                    self._last_resp_t = now
                absence_s = now - self._last_resp_t
                if absence_s >= RESP_ABSENCE_THRESHOLD_S:
                    self.pub.send("vitals/resp_absence", {
                        "absent_s": round(absence_s, 1),
                        "severity": "CRITICAL"
                    })
                    logger.critical(f"RESP ABSENCE: {absence_s:.0f}s!")

                # rPPG heart rate - experimental (VIT-04), only every 5th frame
                if self._frame_n % 5 == 0:
                    rppg_result = self.rppg.estimate(crop)
                    if rppg_result:
                        rppg_result["experimental"] = True
                        self.pub.send("vitals/rppg", rppg_result)

                del frame, crop
                time.sleep(max(0, 0.2 - 0.05))

            except Exception as e:
                logger.error(f"vitals_service error: {e}", exc_info=True)
                time.sleep(0.5)

        self.camera.stop()
        logger.info("vitals_service stopped")


if __name__ == "__main__":
    VitalsService().run()
