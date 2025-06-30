"""Ambient dB SPL monitoring. AUD-03: alert if >threshold for >duration_s."""
import time, logging

logger = logging.getLogger(__name__)


class DBMonitor:
    def __init__(self, threshold=70.0, duration_s=5):
        self._thr  = threshold
        self._dur  = duration_s
        self._over_since = None

    def check(self, db_spl: float, now: float) -> dict | None:
        """Returns alert dict if threshold sustained, else None."""
        if db_spl > self._thr:
            if self._over_since is None:
                self._over_since = now
            elif now - self._over_since >= self._dur:
                return {
                    "type": "loud_event",
                    "severity": "WARN",
                    "db_spl": db_spl,
                    "duration_s": now - self._over_since,
                }
        else:
            self._over_since = None
        return None
