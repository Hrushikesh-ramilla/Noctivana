#!/usr/bin/env python3
"""
BLE GATT server for alert fallback delivery.
ALT-04: queue and deliver CRITICAL alerts via BLE when WiFi down.
Uses BlueZ D-Bus API via python-bluezero.
"""
import time, signal, sys, os, logging, json, queue, threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.utils.zmq_bus      import Subscriber
from src.utils.config_loader import get_config
from src.utils.logger       import setup_logger

logger = setup_logger("ble_service")


class BLEService:
    """
    BLE GATT server wrapping bluezero.
    Notifies connected phone of CRITICAL/WARN alerts.
    """
    SERVICE_UUID  = "12345678-1234-1234-1234-1234567890AB"
    ALERT_CHAR_UUID = "12345678-1234-1234-1234-1234567890AC"

    def __init__(self, cfg_path="config/config.yaml"):
        self.cfg          = get_config(cfg_path)
        self.sub          = Subscriber(["alert/trigger"])
        self._run         = True
        self._queue       = queue.Queue(maxsize=50)
        self._connected   = False
        self._app         = None
        signal.signal(signal.SIGTERM, self._stop)
        signal.signal(signal.SIGINT,  self._stop)

    def _stop(self, *_):
        self._run = False

    def _setup_gatt(self):
        try:
            import bluezero
            from bluezero import peripheral
            self._app = peripheral.Peripheral(
                adapter_addr=None,   # use default adapter
                local_name=self.cfg.get("ble","device_name",default="EdgeWatch"),
                appearance=0x0180    # Generic media device
            )
            self._app.add_service(srv_id=1, uuid=self.SERVICE_UUID, primary=True)
            self._app.add_characteristic(
                srv_id=1, chr_id=1,
                uuid=self.ALERT_CHAR_UUID,
                value=[],
                notifying=False,
                flags=["notify","read"],
            )
            self._app.on_connect    = self._on_connect
            self._app.on_disconnect = self._on_disconnect
            logger.info("BLE GATT service registered")
            return True
        except Exception as e:
            logger.error(f"BLE setup failed: {e}")
            return False

    def _on_connect(self, device):
        self._connected = True
        logger.info(f"BLE device connected: {device}")
        self._flush_queue()

    def _on_disconnect(self, device):
        self._connected = False
        logger.info(f"BLE device disconnected: {device}")

    def _flush_queue(self):
        """Send queued alerts to newly connected device."""
        while not self._queue.empty():
            try:
                payload = self._queue.get_nowait()
                self._notify(payload)
            except queue.Empty:
                break

    def _notify(self, payload_json: str):
        if self._app and self._connected:
            try:
                data = [ord(c) for c in payload_json[:511]]  # max 512 bytes
                self._app.notify_characteristic(1, 1, data)
                logger.info(f"BLE notify sent ({len(data)} bytes)")
            except Exception as e:
                logger.warning(f"BLE notify error: {e}")

    def _keepalive_thread(self):
        """Send keepalive ping every 30s to prevent Android from killing BLE."""
        while self._run:
            if self._connected:
                try:
                    ping = json.dumps({"type": "keepalive", "ts": time.time()})
                    self._notify(ping)
                except Exception:
                    pass
            time.sleep(30)

    def run(self):
        logger.info("ble_service starting...")
        if not self._setup_gatt():
            logger.error("BLE not available. Running in stub mode.")

        # Start keepalive
        t = threading.Thread(target=self._keepalive_thread, daemon=True)
        t.start()

        while self._run:
            try:
                msg = self.sub.recv(timeout_ms=200)
                if msg:
                    data     = msg.get("data", {})
                    severity = data.get("severity","")
                    if severity in ("CRITICAL","WARN"):
                        payload = json.dumps(data)
                        if self._connected:
                            self._notify(payload)
                        else:
                            # Queue for later delivery (ALT-04)
                            try:
                                self._queue.put_nowait(payload)
                            except queue.Full:
                                logger.warning("BLE alert queue full, dropping oldest")
                                self._queue.get_nowait()
                                self._queue.put_nowait(payload)

                if self._app:
                    self._app.publish()

                time.sleep(0.05)

            except Exception as e:
                logger.error(f"ble_service loop error: {e}")
                time.sleep(1.0)

        logger.info("ble_service stopped")


if __name__ == "__main__":
    BLEService().run()
