#!/usr/bin/env python3
"""RGB status LED controller (GPIO PWM, common-cathode)."""
import logging

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    _GPIO_OK = True
except (ImportError, RuntimeError):
    _GPIO_OK = False

# LED state meanings
STATES = {
    "active":  (0, 255, 0),     # green
    "warn":    (255, 165, 0),   # amber
    "critical":(255, 0, 0),     # red
    "setup":   (0, 0, 255),     # blue
    "privacy": (128, 0, 128),   # purple
    "off":     (0, 0, 0),
}


class StatusLED:
    def __init__(self, pin_r=27, pin_g=22, pin_b=10, freq=100):
        self._pins = {"r": pin_r, "g": pin_g, "b": pin_b}
        self._freq = freq
        self._pwm  = {}
        self._state = "off"

    def setup(self):
        if not _GPIO_OK:
            return
        GPIO.setmode(GPIO.BCM)
        for ch, pin in self._pins.items():
            GPIO.setup(pin, GPIO.OUT)
            p = GPIO.PWM(pin, self._freq)
            p.start(0)
            self._pwm[ch] = p
        logger.info("Status LED ready")

    def set_state(self, state: str):
        if state not in STATES:
            logger.warning(f"Unknown LED state: {state}")
            return
        self._state = state
        r, g, b = STATES[state]
        self._set_rgb(r, g, b)
        logger.info(f"LED -> {state}")

    def _set_rgb(self, r, g, b):
        if not self._pwm:
            return
        self._pwm["r"].ChangeDutyCycle(r / 2.55)
        self._pwm["g"].ChangeDutyCycle(g / 2.55)
        self._pwm["b"].ChangeDutyCycle(b / 2.55)

    def cleanup(self):
        self._set_rgb(0, 0, 0)
        if _GPIO_OK:
            GPIO.cleanup(list(self._pins.values()))
