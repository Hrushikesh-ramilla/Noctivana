"""
ZeroMQ message protocol definition.
All messages: {topic: str, ts: float, data: dict}
"""
import json, time, logging

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = {"topic", "ts", "data"}


def encode(topic: str, data: dict) -> tuple:
    """Encode message to (topic_bytes, payload_bytes)."""
    payload = json.dumps({"topic": topic, "ts": time.time(), "data": data})
    return topic.encode(), payload.encode()


def decode(raw_bytes: bytes) -> dict | None:
    """Decode raw ZMQ message bytes to dict."""
    try:
        msg = json.loads(raw_bytes.decode())
        if not REQUIRED_FIELDS.issubset(msg.keys()):
            logger.warning(f"ZMQ message missing fields: {msg.keys()}")
        return msg
    except Exception as e:
        logger.error(f"ZMQ decode error: {e}")
        return None
