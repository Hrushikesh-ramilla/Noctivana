
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


## 2025-06-23 - bh1750 reading 340 lux under desk lamp, 0 with hand over it
- BH1750 auto-range: 340 lux lit, ~0 covered. Working great.


## 2025-06-23 - sgp30 needs 15s baseline warmup, readings stabilize after ~1min
- SGP30 warmup: first 15s gives 0,400. After 1min: 12ppb TVOC, 410 ppm eCO2


## 2025-06-24 - mic not detected, need dtoverlay=googlevoicehat-soundcard
- Tried googlevoicehat overlay first. Wrong device.
- No audio device in arecord -l


## 2025-06-24 - wrong overlay, thats for respeaker. trying i2s-mmap
- googlevoicehat is for ReSpeaker HAT not INMP441
- Trying generic i2s-mmap overlay


## 2025-06-24 - still no audio device showing up in arecord -l
- i2s-mmap also not working. Missing kernel module?
- Trying: sudo modprobe snd-soc-simple-card


## 2025-06-24 - FINALLY: dtoverlay=i2s-mmap + modprobe snd-i2s-hifiberry-dac
- /boot/config.txt: dtoverlay=i2s-mmap
- modprobe snd-soc-simple-card
- card 1: sndrpisimplecar [snd_rpi_simple_card]


## 2025-06-24 - audio capture working! 16khz 16bit mono
- sounddevice device=2 captures cleanly at 16kHz 16bit mono
- RMS ~800 with ambient room noise


## 2025-06-24 - recording 5 sec test audio, sounds correct on playback
- Recorded 5s clip, played back via aplay. Clear mic signal, no distortion.


## 2025-06-24 - add audio config to /boot/config.txt docs
- Documented exact dtoverlay line in rpi_setup.md
- Added modprobe step to avoid forgetting next time


## 2025-06-24 - fixed mic test script, was hardcoded to wrong device index
- device=0 was built-in audio, device=2 is I2S mic
- Added device listing at top of test script


## 2025-06-25 - ir led draws too much current from gpio pin directly
- GPIO pin max ~16mA, IR LED needs ~100mA
- Sourcing a 2N2222 NPN transistor to switch it


## 2025-06-25 - ir led working with transistor switch, nice and bright
- 2N2222: Base via 1kR from GPIO17, Collector drives LED ring
- Can see IR on phone camera, covers full crib area


## 2025-06-25 - ir led gpio control module
- src/hardware/ir_led.py created
- PWM brightness control via RPi.GPIO


## 2025-06-25 - night mode test: turn off lights + enable ir
- BH1750 drops below 5 lux -> enable IR LED -> camera sees crib
- Full darkness test passed, doll visible via phone camera trick

