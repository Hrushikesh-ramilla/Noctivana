"""Alert event data class."""
import time
from dataclasses import dataclass, field, asdict
from typing import List
from src.alert.severity import Severity

@dataclass
class AlertEvent:
    alert_type: str
    severity:   Severity
    sensors:    List[str]
    confidence: float
    value:      float = 0.0
    ts:         float = field(default_factory=time.time)
    message:    str   = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["severity"] = self.severity.value
        return d

    def to_payload(self) -> dict:
        """Return <512 byte JSON-serializable alert payload (ALT-05)."""
        return {
            "ts":         round(self.ts, 3),
            "type":       self.alert_type,
            "severity":   self.severity.value,
            "sensors":    self.sensors[:5],
            "confidence": round(self.confidence, 3),
            "value":      round(self.value, 2),
            "message":    self.message[:120],
        }
