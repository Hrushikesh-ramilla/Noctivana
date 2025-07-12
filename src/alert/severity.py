"""Alert severity levels."""
from enum import Enum

class Severity(str, Enum):
    INFO     = "INFO"
    WARN     = "WARN"
    CRITICAL = "CRITICAL"

SEVERITY_RANK = {Severity.INFO: 0, Severity.WARN: 1, Severity.CRITICAL: 2}
