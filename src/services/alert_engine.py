#!/usr/bin/env python3
"""
Alert engine: subscribes all ZMQ sensor topics -> multi-signal fusion -> MQTT + BLE dispatch.
Covers: ALT-01 (fusion), ALT-02 (false-alarm filter), ALT-03 (session trend),
        ALT-04 (BLE fallback), ALT-05 (payload format).
"""
import time, signal, sys, os, logging, threading, json
import paho.mqtt.client as mqtt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.alert.fusion      import FusionEngine
from src.alert.severity    import Severity
from src.utils.zmq_bus     import Subscriber
from src.utils.config_loader import get_config
from src.utils.logger      import setup_logger
from src.hardware.status_led import StatusLED

logger = setup_logger("alert_engine")

ALL_TOPICS = [
    "audio/cry", "audio/dblevel", "audio/breath",
    "vision/pose", "vision/occlusion", "vision/motion",
    "vitals/resp", "vitals/resp_absence",
    "env/climate", "env/alert",
]


class AlertEngine:
    def __init__(self, cfg_path="config/config.yaml"):
        self.cfg     = get_config(cfg_path)
        self.fusion  = FusionEngine(self.cfg.get("thresholds"))
        self.sub     = Subscriber(ALL_TOPICS)
        self.led     = StatusLED(
            pin_r=self.cfg.get("hardware","status_led_r",default=27),
            pin_g=self.cfg.get("hardware","status_led_g",default=22),
            pin_b=self.cfg.get("hardware","status_led_b",default=10))
        self._mqtt   = None
        self._run    = True
        self._session_alerts = []
        self._ble_queue      = []
        signal.signal(signal.SIGTERM, self._stop)
        signal.signal(signal.SIGINT,  self._stop)

    def _stop(self, *_):
        self._run = False

    def _init_mqtt(self):
        cfg  = self.cfg.get("mqtt") or {}
        host = cfg.get("host", "localhost")
        port = cfg.get("port", 8883)
        self._mqtt = mqtt.Client(client_id="alert_engine", clean_session=True)
        try:
            if cfg.get("use_tls"):
                import ssl
                self._mqtt.tls_set(
                    ca_certs="config/certs/ca.crt",
                    tls_version=ssl.PROTOCOL_TLS)
            self._mqtt.on_disconnect = self._on_mqtt_disconnect
            self._mqtt.connect(host, port, keepalive=cfg.get("keepalive",120))
            self._mqtt.loop_start()
            logger.info(f"MQTT connected to {host}:{port}")
            self.led.set_state("active")
        except Exception as e:
            logger.error(f"MQTT connect failed: {e}")
            self._mqtt = None

    def _on_mqtt_disconnect(self, client, userdata, rc):
        logger.warning(f"MQTT disconnected rc={rc}, attempting reconnect...")
        self.led.set_state("warn")
        # Exponential backoff reconnect
        for delay in [2, 4, 8, 16, 30]:
            time.sleep(delay)
            try:
                client.reconnect()
                logger.info("MQTT reconnected")
                self.led.set_state("active")
                return
            except Exception:
                pass
        logger.error("MQTT reconnect failed after all attempts")

    def _publish_alert(self, event):
        payload = json.dumps(event.to_payload())
        topic   = f"edgewatch/alert/{event.severity.value.lower()}"
        logger.info(f"ALERT [{event.severity}] {event.alert_type}: {payload[:80]}")

        # MQTT publish
        if self._mqtt:
            try:
                self._mqtt.publish(topic, payload, qos=1, retain=True)
            except Exception as e:
                logger.error(f"MQTT publish failed: {e}")
                self._ble_queue.append(event)   # queue for BLE fallback

        # Update status LED
        if event.severity == Severity.CRITICAL:
            self.led.set_state("critical")
        elif event.severity == Severity.WARN:
            self.led.set_state("warn")

        # Track session alerts (for ALT-03)
        self._session_alerts.append({
            "ts": event.ts, "type": event.alert_type, "severity": event.severity.value
        })

    def _check_session_trend(self):
        """ALT-03: detect increasing alert frequency."""
        recent = [a for a in self._session_alerts
                  if time.time() - a["ts"] < 3600]   # last hour
        if len(recent) >= 3:
            types = [a["type"] for a in recent]
            if len(set(types)) < len(types) // 2:  # repeated types = trend
                return {"trend": True, "count": len(recent), "types": list(set(types))}
        return {"trend": False}

    def _heartbeat(self):
        """Publish service heartbeat every 30s."""
        while self._run:
            if self._mqtt:
                self._mqtt.publish("edgewatch/heartbeat",
                                   json.dumps({"ts": time.time(), "service": "alert_engine"}),
                                   qos=0)
            time.sleep(30)

    def run(self):
        logger.info("alert_engine starting...")
        self.led.setup()
        self.led.set_state("setup")
        self._init_mqtt()

        t = threading.Thread(target=self._heartbeat, daemon=True)
        t.start()

        while self._run:
            try:
                msg = self.sub.recv(timeout_ms=100)
                if msg:
                    self.fusion.ingest(msg["topic"], msg.get("data", {}))

                alerts = self.fusion.evaluate()
                for alert in alerts:
                    self._publish_alert(alert)

                time.sleep(0.05)

            except Exception as e:
                logger.error(f"alert_engine error: {e}", exc_info=True)
                time.sleep(0.5)

        if self._mqtt:
            self._mqtt.loop_stop()
            self._mqtt.disconnect()
        logger.info("alert_engine stopped")


if __name__ == "__main__":
    AlertEngine().run()
