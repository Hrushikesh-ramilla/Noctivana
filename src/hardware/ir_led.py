#!/usr/bin/env python3
"""IR LED ring controller. GPIO17 via 2N2222 NPN transistor with PWM."""
import logging

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    _GPIO_OK = True
except (ImportError, RuntimeError):
    _GPIO_OK = False
    logger.warning("RPi.GPIO unavailable - IR LED in simulation mode")


class IRLed:
    def __init__(self, pin=17, pwm_freq=100):
        self._pin  = pin
        self._freq = pwm_freq
        self._pwm  = None
        self._on   = False

    def setup(self):
        if not _GPIO_OK:
            return
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.OUT)
        self._pwm = GPIO.PWM(self._pin, self._freq)
        self._pwm.start(0)
        logger.info(f"IR LED ready on GPIO{self._pin}")

    def enable(self, brightness=1.0):
        brightness = max(0.0, min(1.0, brightness))
        self._on = True
        if self._pwm:
            self._pwm.ChangeDutyCycle(brightness * 100)
        logger.info(f"IR LED ON brightness={brightness:.0%}")

    def disable(self):
        self._on = False
        if self._pwm:
            self._pwm.ChangeDutyCycle(0)
        logger.info("IR LED OFF")

    @property
    def is_on(self):
        return self._on

    def cleanup(self):
        self.disable()
        if _GPIO_OK:
            GPIO.cleanup(self._pin)
