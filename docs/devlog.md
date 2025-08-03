
## 2025-06-23 - enable i2c in raspi-config, reboot needed
- Ran `sudo raspi-config nonint do_i2c 0`
- Verified /dev/i2c-1 exists after reboot


## 2025-06-23 - i2c scan: found 3 devices at 0x44, 0x58, 0x23
- SCD40 @ 0x44 OK
- SGP30 @ 0x58 OK
- BH1750 @ 0x23 OK


## 2025-06-23 - scd40 working: 22.4C, 48pct RH, 812 ppm co2
- First stable reading: 22.4C, 48.1% RH, 812 ppm CO2
- Warmup was ~5min as expected

