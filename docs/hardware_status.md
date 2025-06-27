# Hardware Status - June 27, 2025

| Component | Status | Notes |
|-----------|--------|-------|
| RPi Camera v2 + IR lens | Working | 640x480@25fps, 5fps target for inference |
| INMP441 I2S Mic | Working | 16kHz, dtoverlay=i2s-mmap required |
| Sensirion SCD40 | Working | CO2 warmup 5min then stable |
| SGP30 VOC | Working | 15s warmup, rare zero-read handled with retry |
| BH1750 Light | Working | 0-65535 lux, auto-resolution |
| IR LED Ring | Working | GPIO17 + 2N2222 transistor, PWM brightness |
| Night Mode | Working | Manual exposure 1/30s, gain 4.0 in IR mode |

## Known Hardware Quirks
- SGP30 returns 0 on first read sometimes - mitigated with 3-retry init
- IR mode has 2s camera settling time after switching
- I2S dtoverlay is boot-time only, not hot-pluggable
