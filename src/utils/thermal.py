"""CPU temperature monitoring for Raspberry Pi."""
import logging, time

logger = logging.getLogger(__name__)

TEMP_FILE = "/sys/class/thermal/thermal_zone0/temp"
WARN_C    = 70.0
THROTTLE_C = 75.0


def read_cpu_temp_c() -> float:
    try:
        raw = open(TEMP_FILE).read().strip()
        return int(raw) / 1000.0
    except Exception:
        return 0.0


def check_thermal() -> dict:
    temp = read_cpu_temp_c()
    status = "ok"
    if temp >= THROTTLE_C:
        status = "throttling"
    elif temp >= WARN_C:
        status = "warm"
    return {"temp_c": temp, "status": status}
