"""ZeroMQ pub-sub helpers. All services use XPUB/XSUB proxy pattern."""
import zmq, json, logging, time
from typing import Any

logger = logging.getLogger(__name__)

PROXY_PUB = "tcp://localhost:5555"
PROXY_SUB = "tcp://localhost:5556"


class Publisher:
    def __init__(self, proxy_addr=PROXY_SUB):
        self._ctx    = zmq.Context.instance()
        self._sock   = self._ctx.socket(zmq.PUB)
        self._sock.connect(proxy_addr)
        time.sleep(0.05)  # allow connections to settle

    def send(self, topic: str, data: dict):
        payload = json.dumps({"topic": topic, "ts": time.time(), "data": data})
        self._sock.send_multipart([topic.encode(), payload.encode()])

    def close(self):
        self._sock.close()


class Subscriber:
    def __init__(self, topics: list, proxy_addr=PROXY_PUB):
        self._ctx  = zmq.Context.instance()
        self._sock = self._ctx.socket(zmq.SUB)
        self._sock.connect(proxy_addr)
        for t in topics:
            self._sock.setsockopt_string(zmq.SUBSCRIBE, t)

    def recv(self, timeout_ms=1000):
        if self._sock.poll(timeout_ms):
            _, raw = self._sock.recv_multipart()
            return json.loads(raw.decode())
        return None

    def close(self):
        self._sock.close()
