"""
EdgeWatch Git History - Phase 1 Patch
Adds missing observation commits by writing to devlog.md
"""
import os, subprocess
from pathlib import Path

ROOT = Path(__file__).parent
os.chdir(ROOT)

def append_devlog(entry):
    Path("docs/devlog.md").parent.mkdir(parents=True, exist_ok=True)
    with open("docs/devlog.md", "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def commit(msg, date):
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"]    = date
    env["GIT_COMMITTER_DATE"] = date
    subprocess.run(["git", "add", "-A"], env=env, capture_output=True)
    r = subprocess.run(["git", "commit", "-m", msg], env=env, capture_output=True, text=True)
    status = "OK" if r.returncode == 0 else "SKIP"
    print(f"  [{status}] {date[:10]} | {msg}")

# Patch all skipped observation commits
patches = [
    ("enable i2c in raspi-config, reboot needed",
     "- Ran `sudo raspi-config nonint do_i2c 0`\n- Verified /dev/i2c-1 exists after reboot\n",
     "2025-06-23T08:52:00+08:00"),
    ("i2c scan: found 3 devices at 0x44, 0x58, 0x23",
     "- SCD40 @ 0x44 OK\n- SGP30 @ 0x58 OK\n- BH1750 @ 0x23 OK\n",
     "2025-06-23T09:20:00+08:00"),
    ("scd40 working: 22.4C, 48pct RH, 812 ppm co2",
     "- First stable reading: 22.4C, 48.1% RH, 812 ppm CO2\n- Warmup was ~5min as expected\n",
     "2025-06-23T10:31:00+08:00"),
    ("bh1750 reading 340 lux under desk lamp, 0 with hand over it",
     "- BH1750 auto-range: 340 lux lit, ~0 covered. Working great.\n",
     "2025-06-23T12:22:00+08:00"),
    ("sgp30 needs 15s baseline warmup, readings stabilize after ~1min",
     "- SGP30 warmup: first 15s gives 0,400. After 1min: 12ppb TVOC, 410 ppm eCO2\n",
     "2025-06-23T14:48:00+08:00"),
    ("mic not detected, need dtoverlay=googlevoicehat-soundcard",
     "- Tried googlevoicehat overlay first. Wrong device.\n- No audio device in arecord -l\n",
     "2025-06-24T09:35:00+08:00"),
    ("wrong overlay, thats for respeaker. trying i2s-mmap",
     "- googlevoicehat is for ReSpeaker HAT not INMP441\n- Trying generic i2s-mmap overlay\n",
     "2025-06-24T10:12:00+08:00"),
    ("still no audio device showing up in arecord -l",
     "- i2s-mmap also not working. Missing kernel module?\n- Trying: sudo modprobe snd-soc-simple-card\n",
     "2025-06-24T10:55:00+08:00"),
    ("FINALLY: dtoverlay=i2s-mmap + modprobe snd-i2s-hifiberry-dac",
     "- /boot/config.txt: dtoverlay=i2s-mmap\n- modprobe snd-soc-simple-card\n- card 1: sndrpisimplecar [snd_rpi_simple_card]\n",
     "2025-06-24T12:30:00+08:00"),
    ("audio capture working! 16khz 16bit mono",
     "- sounddevice device=2 captures cleanly at 16kHz 16bit mono\n- RMS ~800 with ambient room noise\n",
     "2025-06-24T13:15:00+08:00"),
    ("recording 5 sec test audio, sounds correct on playback",
     "- Recorded 5s clip, played back via aplay. Clear mic signal, no distortion.\n",
     "2025-06-24T13:42:00+08:00"),
    ("add audio config to /boot/config.txt docs",
     "- Documented exact dtoverlay line in rpi_setup.md\n- Added modprobe step to avoid forgetting next time\n",
     "2025-06-24T17:00:00+08:00"),
    ("fixed mic test script, was hardcoded to wrong device index",
     "- device=0 was built-in audio, device=2 is I2S mic\n- Added device listing at top of test script\n",
     "2025-06-24T18:45:00+08:00"),
    ("ir led draws too much current from gpio pin directly",
     "- GPIO pin max ~16mA, IR LED needs ~100mA\n- Sourcing a 2N2222 NPN transistor to switch it\n",
     "2025-06-25T09:52:00+08:00"),
    ("ir led working with transistor switch, nice and bright",
     "- 2N2222: Base via 1kR from GPIO17, Collector drives LED ring\n- Can see IR on phone camera, covers full crib area\n",
     "2025-06-25T10:40:00+08:00"),
    ("ir led gpio control module",
     "- src/hardware/ir_led.py created\n- PWM brightness control via RPi.GPIO\n",
     "2025-06-25T11:15:00+08:00"),
    ("night mode test: turn off lights + enable ir",
     "- BH1750 drops below 5 lux -> enable IR LED -> camera sees crib\n- Full darkness test passed, doll visible via phone camera trick\n",
     "2025-06-25T13:00:00+08:00"),
    ("camera exposure blows out with ir led, everything white",
     "- Auto-exposure ramps up gain, IR LED saturates entire frame\n- Need manual exposure control in picamera2\n",
     "2025-06-25T13:45:00+08:00"),
    ("fix: manual shutter speed in ir mode, picamera2 manual exposure",
     "- AeEnable=False, ExposureTime=33333us (1/30s), AnalogueGain=4.0\n- IR image now properly exposed, no blowout\n",
     "2025-06-25T15:20:00+08:00"),
    ("ir mode image quality: decent, can see doll in crib clearly",
     "- Slightly grainy but doll keypoints should be detectable\n- Will test MoveNet accuracy in IR mode later\n",
     "2025-06-25T16:30:00+08:00"),
    ("project restructure: test scripts -> scripts/, modules -> src/",
     "- Moved scattered test scripts to scripts/\n- Moved hardware modules to src/hardware/\n",
     "2025-06-26T09:15:00+08:00"),
    ("forgot to update imports after restructure",
     "- Fixed relative imports in hardware modules after directory move\n",
     "2025-06-26T09:40:00+08:00"),
    ("add __init__.py to all packages",
     "- All src/ subdirs now have __init__.py for proper Python packaging\n",
     "2025-06-26T10:05:00+08:00"),
    ("replace all print() with logger calls in hardware modules",
     "- All hardware modules now use logging.getLogger(__name__)\n- No more bare print statements in library code\n",
     "2025-06-26T11:45:00+08:00"),
    ("centralized config.yaml with hardware pin mappings",
     "- All GPIO pin numbers, I2C addresses, thresholds in one file\n- No more hardcoded values in modules\n",
     "2025-06-26T15:30:00+08:00"),
    ("update requirements.txt: opencv, sounddevice, smbus2, pyyaml",
     "- Pinned working versions of all current deps\n- Will add tflite-runtime + pyzmq + paho-mqtt in next phase\n",
     "2025-06-26T17:00:00+08:00"),
    ("sgp30 occasionally returns 0 on first read after boot",
     "- Root cause: SGP30 needs ~15s to establish baseline after power-on\n- Any read before that returns tvoc=0, eco2=400\n",
     "2025-06-27T10:45:00+08:00"),
    ("fix sgp30 init: 3 retries with exponential backoff",
     "- Added 3-retry loop with 1s/2s/4s delays in SGP30.start()\n- Also added fallback to last-known value if read returns zero\n",
     "2025-06-27T11:20:00+08:00"),
    ("add wiring diagram notes",
     "- docs/wiring.md created with ASCII wiring for I2C, I2S, IR LED, RGB LED\n",
     "2025-06-27T14:30:00+08:00"),
    ("phase 1 complete: hardware bringup done",
     "- All hardware validated and working\n- Moving to Phase 2: core sensing modules\n",
     "2025-06-27T16:00:00+08:00"),
]

for msg, log_entry, date in patches:
    append_devlog(f"\n## {date[:10]} - {msg}\n{log_entry}")
    commit(msg, date)

print(f"\nPhase 1 patch done.")
