#!/usr/bin/env python3
"""
Environmental sensor service.
Polls SCD40+SGP30+BH1750 at 1Hz, publishes to ZMQ, checks alert thresholds.
Handles: ENV-01 (temp/humidity), ENV-02 (CO2), ENV-03 (VOC), ENV-04 (dB log),
         ENV-05 (real-time display + local logging)
"""
import time, logging, signal, sys, os, csv
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.hardware.sensors import SensorHub
from src.utils.zmq_bus   import Publisher
from src.utils.config_loader import get_config
from src.utils.logger    import setup_logger

logger = setup_logger("env_service")


class EnvService:
    def __init__(self, cfg_path="config/config.yaml"):
        self.cfg   = get_config(cfg_path)
        self.hub   = SensorHub(bus_number=self.cfg.get("hardware","i2c_bus",default=1))
        self.pub   = Publisher()
        self._run  = True
        self._session_csv = None
        self._csv_writer  = None
        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT,  self._shutdown)

    def _shutdown(self, *_):
        logger.info("env_service shutting down")
        self._run = False

    def _open_csv(self, session_id):
        csv_dir = self.cfg.get("paths","session_csv_dir",default="/tmp/edgewatch")
        os.makedirs(csv_dir, exist_ok=True)
        path = os.path.join(csv_dir, f"env_{session_id}.csv")
        f    = open(path, "w", newline="")
        w    = csv.DictWriter(f, fieldnames=["ts","temp_c","humidity","co2_ppm","tvoc_ppb","lux"])
        w.writeheader()
        return f, w

    def _check_thresholds(self, reading: dict):
        """Return list of (severity, alert_type, value) tuples."""
        alerts = []
        t  = self.cfg.get("thresholds")
        tc = reading.get("temp_c")
        rh = reading.get("humidity")
        co = reading.get("co2_ppm")
        voc= reading.get("tvoc_ppb")

        if tc is not None:
            if tc > t.get("temp_high_c", 28):
                alerts.append(("WARN","temp_high", tc))
            elif tc < t.get("temp_low_c", 16):
                alerts.append(("WARN","temp_low", tc))

        if rh is not None:
            if rh > t.get("humidity_high_pct", 65):
                alerts.append(("WARN","humidity_high", rh))
            elif rh < t.get("humidity_low_pct", 30):
                alerts.append(("WARN","humidity_low", rh))

        if co is not None:
            if co > t.get("co2_critical_ppm", 2000):
                alerts.append(("CRITICAL","co2_critical", co))
            elif co > t.get("co2_warn_ppm", 1000):
                alerts.append(("WARN","co2_high", co))

        return alerts

    def run(self):
        logger.info("env_service starting...")
        self.hub.start_all()
        session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self._session_csv, self._csv_writer = self._open_csv(session_id)

        while self._run:
            try:
                reading = self.hub.poll()
                reading["ts"] = time.time()

                # Publish to ZMQ
                self.pub.send("env/climate", reading)

                # Threshold check -> publish alerts
                for sev, atype, val in self._check_thresholds(reading):
                    self.pub.send("env/alert", {
                        "severity": sev,
                        "type": atype,
                        "value": val,
                        "sensor": "env"
                    })
                    logger.warning(f"ENV alert: {sev} {atype} = {val}")

                # Log to CSV
                if self._csv_writer:
                    self._csv_writer.writerow({
                        "ts":       reading["ts"],
                        "temp_c":   reading.get("temp_c"),
                        "humidity": reading.get("humidity"),
                        "co2_ppm":  reading.get("co2_ppm"),
                        "tvoc_ppb": reading.get("tvoc_ppb"),
                        "lux":      reading.get("lux"),
                    })

                time.sleep(1.0)

            except Exception as e:
                logger.error(f"env_service loop error: {e}")
                time.sleep(1.0)

        self.hub.close()
        if self._session_csv:
            self._session_csv.close()
        logger.info("env_service stopped")


if __name__ == "__main__":
    EnvService().run()
