#!/usr/bin/env python3
"""
Audio monitoring service.
Captures I2S mic -> MFCC -> YAMNet cry classification,
dB monitoring, and acoustic breath detection.
Covers: AUD-01, AUD-02, AUD-03, AUD-05
"""
import time, signal, sys, os, logging, collections
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.hardware.mic        import Microphone
from src.audio.feature_extract import compute_yamnet_input, rms_to_db
from src.audio.cry_classifier  import CryClassifier
from src.audio.db_monitor      import DBMonitor
from src.audio.breath_detector import BreathDetector
from src.utils.zmq_bus         import Publisher
from src.utils.config_loader   import get_config
from src.utils.logger          import setup_logger

logger = setup_logger("audio_service")

WINDOW_S = 0.96
HOP_S    = 0.48


class AudioService:
    def __init__(self, cfg_path="config/config.yaml"):
        self.cfg        = get_config(cfg_path)
        self.mic        = Microphone(
            device_index=self.cfg.get("hardware","mic_device_index",default=2))
        self.classifier = CryClassifier(
            model_path=self.cfg.get("paths","models_dir",default="models")+"/yamnet.tflite")
        self.db_mon     = DBMonitor(
            threshold=self.cfg.get("thresholds","db_alert_threshold",default=70.0),
            duration_s=self.cfg.get("thresholds","db_alert_duration_s",default=5))
        self.breath     = BreathDetector()
        self.pub        = Publisher()
        self._run       = True
        self._last_infer_t = 0
        signal.signal(signal.SIGTERM, self._stop)
        signal.signal(signal.SIGINT,  self._stop)

    def _stop(self, *_):
        self._run = False

    def run(self):
        logger.info("audio_service starting...")
        self.mic.start()
        time.sleep(1.0)  # let mic settle

        while self._run:
            try:
                now = time.time()
                # Cry classification at 2/sec
                if now - self._last_infer_t >= HOP_S:
                    audio = self.mic.read_window(WINDOW_S)
                    yamnet_input = compute_yamnet_input(audio)

                    result = self.classifier.infer(yamnet_input)
                    if result:
                        logger.info(f"Cry detected: {result['cry_type']} conf={result['confidence']:.2f}")
                        self.pub.send("audio/cry", result)
                    self._last_infer_t = now

                # dB level at 4/sec
                db = rms_to_db(self.mic.read_window(0.25))
                self.pub.send("audio/dblevel", {"db_spl": db, "ts": now})
                db_alert = self.db_mon.check(db, now)
                if db_alert:
                    self.pub.send("audio/alert", db_alert)

                # Acoustic breath check at 0.5/sec
                breath_ok = self.breath.check(self.mic.read_window(2.0), now)
                self.pub.send("audio/breath", {"detected": breath_ok, "ts": now})
                if not breath_ok:
                    logger.warning("Acoustic breath signal absent")

                time.sleep(0.1)

            except Exception as e:
                logger.error(f"audio_service loop error: {e}")
                time.sleep(0.5)

        self.mic.stop()
        logger.info("audio_service stopped")


if __name__ == "__main__":
    AudioService().run()
