"""
Multi-signal fusion evaluator. ALT-01, ALT-02.
Evaluates buffered sensor events against rule set.
"""
import time, logging, collections
from src.alert.severity import Severity
from src.alert.event    import AlertEvent

logger = logging.getLogger(__name__)

WINDOW_S        = 10.0  # event buffer window
RATE_LIMIT_S    = 60.0  # max 1 CRITICAL per type per 60s


class FusionEngine:
    def __init__(self, config: dict = None):
        self._cfg         = config or {}
        self._buffers     = collections.defaultdict(list)
        self._last_alert  = {}   # {alert_type: timestamp}
        self._logger      = logger

    def ingest(self, topic: str, data: dict, now: float = None):
        """Add a sensor event to the fusion buffer."""
        now = now or time.time()
        self._buffers[topic].append({"ts": now, "data": data})
        # Prune old events
        cutoff = now - WINDOW_S
        self._buffers[topic] = [e for e in self._buffers[topic] if e["ts"] > cutoff]

    def _recent(self, topic, secs=WINDOW_S) -> list:
        cutoff = time.time() - secs
        return [e for e in self._buffers.get(topic, []) if e["ts"] > cutoff]

    def _rate_limited(self, alert_type: str) -> bool:
        last = self._last_alert.get(alert_type, 0)
        return (time.time() - last) < RATE_LIMIT_S

    def _mark_alerted(self, alert_type: str):
        self._last_alert[alert_type] = time.time()

    def evaluate(self) -> list[AlertEvent]:
        """Evaluate all fusion rules, return list of AlertEvents to dispatch."""
        alerts = []
        now    = time.time()

        # Rule 1: Prone position CRITICAL
        # Condition: prone detected + motion=still/low + no caregiver
        prone_events  = self._recent("vision/pose", secs=10)
        motion_events = self._recent("vision/motion", secs=5)
        if prone_events and not self._rate_limited("prone_critical"):
            prone_data = prone_events[-1]["data"]
            if prone_data.get("position") == "prone" and prone_data.get("prone_sustained_s", 0) >= 5:
                # Suppress if restless motion (baby actively rolling)
                restless = any(e["data"].get("level") == "restless" for e in motion_events)
                if not restless:
                    alerts.append(AlertEvent(
                        alert_type="prone_position",
                        severity=Severity.CRITICAL,
                        sensors=["camera/pose"],
                        confidence=prone_data.get("confidence", 0.8),
                        message="Infant detected in prone (face-down) position",
                    ))
                    self._mark_alerted("prone_critical")
                    logger.critical("FUSION: prone_position CRITICAL")

        # Rule 2: Face occlusion CRITICAL
        occ_events = self._recent("vision/occlusion", secs=5)
        if occ_events and not self._rate_limited("face_occlusion"):
            occ = occ_events[-1]["data"]
            if occ.get("occluded") and occ.get("sustained_s", 0) >= 3:
                alerts.append(AlertEvent(
                    alert_type="face_occlusion",
                    severity=Severity.CRITICAL,
                    sensors=["camera/occlusion"],
                    confidence=0.85,
                    message="Face occlusion detected - possible airway obstruction",
                ))
                self._mark_alerted("face_occlusion")
                logger.critical("FUSION: face_occlusion CRITICAL")

        # Rule 3: Respiratory absence CRITICAL
        resp_absence = self._recent("vitals/resp_absence", secs=20)
        if resp_absence and not self._rate_limited("resp_absence"):
            absent_s = resp_absence[-1]["data"].get("absent_s", 0)
            # Corroborate: motion should be still too
            still = any(e["data"].get("level") == "still" for e in motion_events)
            if absent_s >= 15 and still:
                alerts.append(AlertEvent(
                    alert_type="resp_absence",
                    severity=Severity.CRITICAL,
                    sensors=["camera/vitals", "audio/breath"],
                    confidence=0.9,
                    value=absent_s,
                    message=f"No respiratory motion detected for {absent_s:.0f}s",
                ))
                self._mark_alerted("resp_absence")
                logger.critical(f"FUSION: resp_absence {absent_s:.0f}s CRITICAL")

        # Rule 4: Environmental WARN alerts
        env_events = self._recent("env/climate", secs=60)
        if env_events:
            env = env_events[-1]["data"]
            tc  = env.get("temp_c")
            if tc and tc > 28.0 and not self._rate_limited("temp_high"):
                alerts.append(AlertEvent(
                    alert_type="temp_high",
                    severity=Severity.WARN,
                    sensors=["env/scd40"],
                    confidence=1.0,
                    value=tc,
                    message=f"Room temperature {tc:.1f}°C above safe range",
                ))
                self._mark_alerted("temp_high")

            co2 = env.get("co2_ppm")
            if co2 and co2 > 1000 and not self._rate_limited("co2_high"):
                sev = Severity.CRITICAL if co2 > 2000 else Severity.WARN
                alerts.append(AlertEvent(
                    alert_type="co2_high",
                    severity=sev,
                    sensors=["env/scd40"],
                    confidence=1.0,
                    value=co2,
                    message=f"CO2 level {co2} ppm - ventilation needed",
                ))
                self._mark_alerted("co2_high")

        # Rule 5: Loud event WARN
        db_events = self._recent("audio/dblevel", secs=5)
        if db_events and not self._rate_limited("loud_event"):
            avg_db = sum(e["data"].get("db_spl",0) for e in db_events) / len(db_events)
            if avg_db > 70.0 and len(db_events) >= 3:   # sustained
                alerts.append(AlertEvent(
                    alert_type="loud_event",
                    severity=Severity.WARN,
                    sensors=["audio/dblevel"],
                    confidence=0.9,
                    value=avg_db,
                    message=f"Sustained loud noise {avg_db:.0f} dB",
                ))
                self._mark_alerted("loud_event")

        return alerts
