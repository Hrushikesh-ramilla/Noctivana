#!/usr/bin/env python3
"""I2C sensor hub: SCD40, SGP30, BH1750."""
import smbus2, time, logging

logger = logging.getLogger(__name__)


class SCD40:
    ADDR = 0x44

    def __init__(self, bus):
        self._b = bus
        self._ready = False

    def _cmd(self, b, delay=0.005):
        self._b.write_i2c_block_data(self.ADDR, b[0], list(b[1:]))
        time.sleep(delay)

    def start(self):
        self._cmd([0x3F,0x86]); time.sleep(0.5)
        self._cmd([0x21,0xB1]); time.sleep(0.05)
        self._ready = True
        logger.info("SCD40 started")

    def read(self):
        if not self._ready:
            return None
        try:
            self._b.write_i2c_block_data(self.ADDR, 0xE4, [0xB8])
            time.sleep(0.001)
            rdy = self._b.read_i2c_block_data(self.ADDR, 0, 3)
            if not (rdy[1] & 0x07):
                return None
            self._b.write_i2c_block_data(self.ADDR, 0xEC, [0x05])
            time.sleep(0.001)
            d = self._b.read_i2c_block_data(self.ADDR, 0, 9)
            co2  = (d[0]<<8)|d[1]
            temp = -45 + 175*((d[3]<<8)|d[4])/65535.0
            rh   = 100*((d[6]<<8)|d[7])/65535.0
            return co2, round(temp,2), round(rh,2)
        except Exception as e:
            logger.warning(f"SCD40 read error: {e}")
            return None

    def stop(self):
        try: self._cmd([0x3F,0x86])
        except Exception: pass


class SGP30:
    ADDR = 0x58

    def __init__(self, bus):
        self._b = bus
        self._tvoc = 0
        self._eco2 = 400

    def start(self):
        for attempt in range(3):
            try:
                self._b.write_i2c_block_data(self.ADDR, 0x20, [0x03])
                time.sleep(0.01)
                logger.info("SGP30 started")
                return
            except Exception as e:
                logger.warning(f"SGP30 init attempt {attempt+1} failed: {e}")
                time.sleep(2**attempt)
        raise RuntimeError("SGP30 init failed after retries")

    def read(self):
        try:
            self._b.write_i2c_block_data(self.ADDR, 0x20, [0x08])
            time.sleep(0.012)
            d = self._b.read_i2c_block_data(self.ADDR, 0, 6)
            t = (d[0]<<8)|d[1]
            e = (d[3]<<8)|d[4]
            if t == 0 and e == 0:
                logger.warning("SGP30 zero read, using last known")
                return self._tvoc, self._eco2
            self._tvoc, self._eco2 = t, e
            return t, e
        except Exception as e:
            logger.warning(f"SGP30 read error: {e}")
            return self._tvoc, self._eco2


class BH1750:
    ADDR = 0x23

    def __init__(self, bus):
        self._b = bus

    def start(self):
        self._b.write_byte(self.ADDR, 0x10)
        time.sleep(0.12)
        logger.info("BH1750 started")

    def read_lux(self):
        try:
            d = self._b.read_i2c_block_data(self.ADDR, 0, 2)
            return round(((d[0]<<8)+d[1])/1.2, 1)
        except Exception as e:
            logger.warning(f"BH1750 read error: {e}")
            return 0.0


class SensorHub:
    """Manages all I2C sensors on the bus."""

    def __init__(self, bus_number=1):
        self._bus = smbus2.SMBus(bus_number)
        self.scd40   = SCD40(self._bus)
        self.sgp30   = SGP30(self._bus)
        self.bh1750  = BH1750(self._bus)

    def start_all(self):
        self.scd40.start()
        self.sgp30.start()
        self.bh1750.start()

    def poll(self):
        scd = self.scd40.read()
        tvoc, eco2 = self.sgp30.read()
        lux = self.bh1750.read_lux()
        return {
            "co2_ppm":  scd[0] if scd else None,
            "temp_c":   scd[1] if scd else None,
            "humidity": scd[2] if scd else None,
            "tvoc_ppb": tvoc,
            "eco2_ppm": eco2,
            "lux":      lux,
        }

    def close(self):
        self.scd40.stop()
        self._bus.close()
