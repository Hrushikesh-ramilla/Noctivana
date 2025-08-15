
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


## 2025-06-25 - camera exposure blows out with ir led, everything white
- Auto-exposure ramps up gain, IR LED saturates entire frame
- Need manual exposure control in picamera2


## 2025-06-25 - fix: manual shutter speed in ir mode, picamera2 manual exposure
- AeEnable=False, ExposureTime=33333us (1/30s), AnalogueGain=4.0
- IR image now properly exposed, no blowout


## 2025-06-25 - ir mode image quality: decent, can see doll in crib clearly
- Slightly grainy but doll keypoints should be detectable
- Will test MoveNet accuracy in IR mode later


## 2025-06-26 - project restructure: test scripts -> scripts/, modules -> src/
- Moved scattered test scripts to scripts/
- Moved hardware modules to src/hardware/


## 2025-06-26 - forgot to update imports after restructure
- Fixed relative imports in hardware modules after directory move


## 2025-06-26 - add __init__.py to all packages
- All src/ subdirs now have __init__.py for proper Python packaging


## 2025-06-26 - replace all print() with logger calls in hardware modules
- All hardware modules now use logging.getLogger(__name__)
- No more bare print statements in library code


## 2025-06-26 - centralized config.yaml with hardware pin mappings
- All GPIO pin numbers, I2C addresses, thresholds in one file
- No more hardcoded values in modules


## 2025-06-26 - update requirements.txt: opencv, sounddevice, smbus2, pyyaml
- Pinned working versions of all current deps
- Will add tflite-runtime + pyzmq + paho-mqtt in next phase


## 2025-06-27 - sgp30 occasionally returns 0 on first read after boot
- Root cause: SGP30 needs ~15s to establish baseline after power-on
- Any read before that returns tvoc=0, eco2=400


## 2025-06-27 - fix sgp30 init: 3 retries with exponential backoff
- Added 3-retry loop with 1s/2s/4s delays in SGP30.start()
- Also added fallback to last-known value if read returns zero


## 2025-06-27 - add wiring diagram notes
- docs/wiring.md created with ASCII wiring for I2C, I2S, IR LED, RGB LED


## 2025-06-27 - phase 1 complete: hardware bringup done
- All hardware validated and working
- Moving to Phase 2: core sensing modules


## 2025-06-28 - pip install pyzmq, zeromq test scripts
- Installed pyzmq 26.0.3
- Basic pub/sub test: publisher -> subscriber over localhost:5555


## 2025-06-28 - zmq topic-based filtering test
- Topics as byte prefixes work correctly
- Subscriber only gets messages matching its topic prefix


## 2025-06-28 - env service config thresholds
- temp_high: 28C, temp_low: 16C, co2_warn: 1000ppm, co2_crit: 2000ppm
- all read from config.yaml


## 2025-06-28 - env zmq test
- Subscriber script tested, receives env/climate messages correctly
- JSON payload format confirmed working


## 2025-06-28 - timestamps in zmq messages
- Added ISO8601 ts field to all messages using time.time()
- Standardized across all future services


## 2025-06-29 - YAMNet download
- Downloaded yamnet.tflite from TFHub (917KB)
- Added models/README.md with source and license info


## 2025-06-29 - models gitignore
- Decided .tflite files under 5MB will be committed (yamnet=917KB, movenet=3.2MB)
- Updated .gitignore to exclude only .bin files


## 2025-06-29 - first YAMNet inference attempt
- yamnet.tflite loaded OK
- Ran on 0.96s audio window
- Result: classifying everything as Speech 99%
- Something is wrong with input format


## 2025-06-29 - YAMNet input normalization bug
- Was passing raw int16 (range -32768..32767) directly
- YAMNet expects float32 in range [-1.0, 1.0]
- Fix: divide by 32768.0 before inference
- Now getting Speech:0.4, Baby cry:0.3, Music:0.1 on test clip


## 2025-06-30 - YAMNet on Pi latency
- Inference: ~120ms per 0.96s window on Pi4
- That's well within the 3s classification latency budget (AUD-01)
- Running at 2 inferences/sec with 0.48s hop


## 2025-06-30 - YAMNet top-5 output
- Output tensor shape: (521,) - 521 audio classes
- Need to map Baby cry (index ~22), Screaming (index ~80) etc
- Label CSV needed for proper mapping


## 2025-06-30 - breath detection issue
- Bandpass filter 0.2-2Hz picks up AC hum (50Hz harmonics leaking through?)
- Getting false 'breath detected' from electrical noise
- Increased filter order and added energy threshold


## 2025-06-30 - breath detection accepted as supplementary
- Acoustic breath is fallback to optical flow vitals
- Will not rely on it for primary detection


## 2025-07-01 - audio service threading
- Added separate threads for cry inference, db monitoring
- Race condition immediately on shared mic buffer


## 2025-07-01 - threading race condition
- Two threads reading mic._buf simultaneously
- One gets partial write during callback update
- Fix: replace list with collections.deque(maxlen=N) + threading.Lock


## 2025-07-02 - MoveNet download
- movenet_lightning.tflite downloaded from TFHub
- 3.2MB INT8 quantized
- Input: [1,192,192,3] uint8 | Output: [1,1,17,3] keypoints


## 2025-07-02 - MoveNet runs on Pi
- ~100ms per frame at 192x192 input
- 10fps possible in theory, 5fps our target
- BUT: detecting my desk chair as a person?? Keypoints all over furniture


## 2025-07-02 - ROI cropping helps
- After cropping to crib area MoveNet stops detecting furniture
- Much cleaner keypoints, only seeing doll/infant object


## 2025-07-02 - keypoint visualization
- Overlaid keypoints on frame with cv2.circle
- Saved to debug/ folder
- Helps identify which keypoints are reliable from ceiling angle
- Back keypoints (shoulders, hips) visible when supine; face when prone


## 2025-07-02 - debug/ gitignore
- Accidentally committed some test jpg frames
- Added *.jpg to .gitignore and git rm --cached


## 2025-07-03 - first classifier test with doll
- Supine: works reliably (face up, shoulders visible)
- Prone: works (face hidden, back keypoints up)
- Side: garbage - shoulder/hip angle ambiguous from top-down view
- Side detection will be lowest priority


## 2025-07-03 - camera resource leak
- On SIGTERM vision service exits but camera fd not released
- picamera2 stays open, next launch fails
- Fix: add atexit handler + explicit camera.stop() in try/finally


## 2025-07-03 - memory baseline
- vision_service with MoveNet: 580MB RSS
- Within budget (600MB allocated)
- psutil.Process().memory_info().rss


## 2025-07-05 - optical flow resp rate garbage
- Running on full frame: motion vectors from everything (fan, person moving)
- Getting 5-60 bpm randomly - useless
- Need to isolate chest ROI using MoveNet pose keypoints


## 2025-07-05 - optical flow on chest roi
- Getting some periodic signal now!
- Still very noisy - values jumping ±10 bpm
- 30-second averaging window helps


## 2025-07-06 - filtered resp signal
- Bandpass filter output is much cleaner
- Dominant frequency in 0.15-1Hz range now detected reliably
- Estimated 18-35 bpm range (physiological for infant)


## 2025-07-06 - resp rate stable-ish
- With EMA alpha=0.3: ±5 bpm from metronome reference at 30 bpm
- Target is ±4 bpm in 80% of windows - close but not there


## 2025-07-07 - vitals dependency on vision
- vitals_service needs pose keypoints from vision_service for chest ROI
- Can't import directly (separate processes)
- Solution: vitals subscribes to vision/pose topic and caches latest keypoints


## 2025-07-07 - first multi-service test
- Started audio, vision, vitals, env simultaneously
- All publish to ZMQ without conflict
- ZMQ proxy needed next to route messages between subscribers


## 2025-07-08 - night mode works
- BH1750 drops below 5 lux -> IR LED on -> camera switches to manual exposure
- Can see doll in complete darkness


## 2025-07-08 - MoveNet accuracy drops in IR mode
- Normal mode: ~95% keypoint confidence
- IR mode: ~55% keypoint confidence
- Grainy IR image loses fine detail
- Need to improve contrast before inference


## 2025-07-08 - CLAHE in IR mode
- CLAHE clipLimit=3.0 gives better local contrast
- MoveNet accuracy in IR: ~75% vs ~95% day
- Acceptable for monitoring, especially for prone/occlusion


## 2025-07-08 - occlusion first results
- Blanket over face: triggers correctly after 3s
- But: baby turning head sideways = false positive
- Head turn: face keypoints drop but body still visible
- Need to distinguish head turn from actual blockage


## 2025-07-09 - head turn guard
- If body keypoints invisible too = person is face-down but also rolled
- If body visible + face hidden = likely actual occlusion
- Added body_mean > 0.1 guard for daytime mode


## 2025-07-09 - occlusion test results
- 8/10 detected with various blanket placements
- 2 misses: very thin/translucent blanket (keypoints visible through it)


## 2025-07-10 - vision_service refactor
- File growing to 400+ lines
- Extract pose.py, occlusion.py, motion.py, night_mode.py
- vision_service.py becomes thin orchestrator


## 2025-07-10 - import hell after refactor
- Circular import: vision_service imports OcclusionDetector which imported Camera
- Fixed by removing Camera from occlusion.py (passes frame directly)


## 2025-07-10 - FPS measurement
- Average 5.2fps with all vision features enabled
- Barely above 5fps target (NFR-P2)
- Need to keep careful eye on this


## 2025-07-11 - false resp absence
- Baby rolling over = optical flow spike then quiescence = 'no breathing'
- Suppression: if vision/motion shows restless within last 10s, skip absence alarm


## 2025-06-28 - basic zmq pub-sub working on localhost:5555
- PUB socket on tcp://localhost:5555 sending hello every 1s
- SUB socket receives correctly. ZMQ working.


## 2025-06-28 - zmq topic-based filtering test
- Topics work as byte-prefix filters
- SUB('env') only gets env/climate, not audio/cry


## 2025-06-28 - env service config: threshold values from config.yaml
- All thresholds read from config.yaml
- No hardcoded values in service code


## 2025-06-28 - env service publishes to zmq, tested with subscriber script
- Test subscriber receives env/climate messages at 1Hz
- JSON payload: temp_c, humidity, co2_ppm, tvoc_ppb, lux


## 2025-06-28 - add timestamp to all zmq messages, iso8601 format
- Added ts: time.time() field to all messages
- Alert engine can calculate latency from ts field


## 2025-06-29 - add models/ to gitignore, too large for git
- Actually yamnet.tflite is only 917KB - commit it
- Updated .gitignore: only exclude .bin, keep .tflite < 5MB


## 2025-06-29 - yamnet label map csv
- yamnet_labels.csv added to models/ directory
- 521 audio class labels


## 2025-06-29 - first yamnet inference attempt, classifying everything as 'speech'
- YAMNet loaded OK, inference runs in ~120ms
- BUT all results: Speech: 0.97, everything else < 0.01
- Input normalization is wrong


## 2025-06-29 - fix: yamnet expects [-1,1] float, was passing uint16
- Mic records int16 range -32768..32767
- YAMNet expects float32 in [-1.0, 1.0]
- Fix: audio.astype(float32) / 32768.0
- Now: Baby cry: 0.41, Speech: 0.28, Silence: 0.12 on test clip


## 2025-06-29 - cry detection test - picks up baby cry but also triggers on cat/alarm sounds
- Playing YouTube baby cry: correctly detected hunger_cry
- Playing alarm clock: also triggers (alarm class similar freq)
- Need confidence threshold filtering


## 2025-06-30 - yamnet on pi: inference takes ~120ms per 0.96s window, good
- Pi4 inference: 115-125ms average
- 0.96s audio window = run ~8/sec theoretical max
- At 2/sec (HOP=0.48s) we use 25% of latency budget


## 2025-06-30 - yamnet top-5 classes output, need to map to our cry categories
- Top 5 output is enough, need label->category mapping
- Added cry_mapping.yaml for audio classifier


## 2025-06-30 - audio service runs in loop, 0.96s windows with 0.48s overlap
- 0.48s hop gives 2 classifications/sec
- Good real-time response for cry detection


## 2025-06-30 - audio_service publishing to zmq topic audio/cry, tested
- ZMQ subscriber confirms audio/cry messages arriving
- Payload: {cry_type, confidence, top_label, top3}


## 2025-06-30 - breath detection is really noisy, picking up AC hum as breathing
- Bandpass filter catching 50Hz electrical hum harmonics
- Even with cutoff at 2Hz, some interference
- Will treat acoustic breath as secondary to optical flow


## 2025-06-30 - add bandpass filter 0.2-2hz for breath acoustic detection
- Butterworth order 2, bandpass 0.2-2.0Hz for respiration range
- Energy threshold: >1e-4 RMS = breath detected

