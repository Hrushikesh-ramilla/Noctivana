#!/usr/bin/env python3
"""
Session manager: auto-detect sleep sessions and log to SQLite.
Covers: SES-01 (auto-detect), SES-02 (encrypted storage), SES-03 (CSV export).
"""
import time, signal, sys, os, logging, json, csv
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.utils.zmq_bus      import Subscriber
from src.utils.db           import SessionDB
from src.utils.config_loader import get_config
from src.utils.logger       import setup_logger

logger = setup_logger("session_manager")

STILL_THRESHOLD_S = 300   # 5 min still + no cry = session start
STATE_IDLE        = "IDLE"
STATE_MONITORING  = "MONITORING"
STATE_ENDED       = "ENDED"


class SessionManager:
    def __init__(self, cfg_path="config/config.yaml"):
        self.cfg       = get_config(cfg_path)
        self.db        = SessionDB(self.cfg.get("paths","db_path",default="edgewatch.db"))
        self.sub       = Subscriber([
            "vision/motion", "audio/cry", "vision/pose",
            "env/climate", "alert/trigger"
        ])
        self._run          = True
        self._state        = STATE_IDLE
        self._session_id   = None
        self._still_since  = None
        self._env_buffer   = []
        self._alert_count  = {}
        signal.signal(signal.SIGTERM, self._stop)
        signal.signal(signal.SIGINT,  self._stop)

    def _stop(self, *_):
        self._run = False

    def _start_session(self):
        self._session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.db.start_session(self._session_id)
        self._state = STATE_MONITORING
        logger.info(f"Sleep session started: {self._session_id}")

    def _end_session(self):
        if not self._session_id:
            return
        self.db.end_session(self._session_id)
        self._export_csv()
        logger.info(f"Session ended: {self._session_id}")
        self._state = STATE_IDLE
        self._session_id = None
        self._still_since = None

    def _export_csv(self):
        """SES-03: Export session to CSV."""
        if not self._session_id:
            return
        csv_dir = self.cfg.get("paths","session_csv_dir",default="/tmp/edgewatch")
        os.makedirs(csv_dir, exist_ok=True)
        path = os.path.join(csv_dir, f"session_{self._session_id}.csv")
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["ts","type","severity","value"])
            for row in self.db.get_session_alerts(self._session_id):
                w.writerow(row)
        logger.info(f"Session CSV exported: {path}")

    def run(self):
        logger.info("session_manager starting...")
        now = time.time()

        while self._run:
            try:
                msg = self.sub.recv(timeout_ms=500)
                now = time.time()

                if msg:
                    topic = msg.get("topic","")
                    data  = msg.get("data",{})

                    # Session start detection (SES-01)
                    if topic == "vision/motion":
                        level = data.get("level","")
                        if level == "still":
                            if self._still_since is None:
                                self._still_since = now
                            elif (now - self._still_since >= STILL_THRESHOLD_S
                                  and self._state == STATE_IDLE):
                                self._start_session()
                        elif level == "restless":
                            self._still_since = None
                            if self._state == STATE_MONITORING:
                                # Check if waking up (sustained restless + cry)
                                pass

                    # Log events during session
                    if self._state == STATE_MONITORING and self._session_id:
                        if topic == "env/climate":
                            self.db.log_env(self._session_id, data)
                        elif topic == "alert/trigger":
                            self.db.log_alert(self._session_id, data)

                time.sleep(0.1)

            except Exception as e:
                logger.error(f"session_manager error: {e}")
                time.sleep(1.0)

        logger.info("session_manager stopped")


if __name__ == "__main__":
    SessionManager().run()
