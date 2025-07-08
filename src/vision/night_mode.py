"""
Night mode controller: auto-switch IR mode based on BH1750 lux.
VIS-03: IR when lux < threshold.
"""
import time, logging
import smbus2

logger = logging.getLogger(__name__)

LUX_THRESHOLD = 5.0   # lux below this = night
TRANSITION_BUFFER_S = 1.5  # seconds to buffer during IR switch


class NightModeController:
    def __init__(self, lux_threshold=LUX_THRESHOLD, bus_number=1):
        self._thr         = lux_threshold
        self._night       = False
        self._last_lux    = 999.0
        self._trans_until = 0.0
        try:
            self._bus = smbus2.SMBus(bus_number)
            self._bus.write_byte(0x23, 0x10)
            time.sleep(0.12)
            logger.info("NightModeController: BH1750 ready")
        except Exception as e:
            self._bus = None
            logger.warning(f"BH1750 unavailable, night mode manual: {e}")

    def _read_lux(self) -> float:
        if self._bus is None:
            return 999.0
        try:
            d = self._bus.read_i2c_block_data(0x23, 0, 2)
            return ((d[0]<<8)+d[1])/1.2
        except Exception:
            return self._last_lux

    def should_enable(self) -> bool:
        """Returns True if IR mode should be active."""
        lux = self._read_lux()
        self._last_lux = lux
        new_night = lux < self._thr
        if new_night != self._night:
            self._night       = new_night
            self._trans_until = time.time() + TRANSITION_BUFFER_S
            logger.info(f"Night mode {'ON' if new_night else 'OFF'} (lux={lux:.1f})")
        return self._night

    def in_transition(self) -> bool:
        """True during IR transition - suppress alerts briefly."""
        return time.time() < self._trans_until
