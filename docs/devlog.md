
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


## 2025-06-30 - breath detection better but still not great, will rely on vitals module
- Acoustic breath = supplementary AUD-02 feature
- Primary respiratory monitoring = optical flow (vitals_service)


## 2025-07-01 - refactor audio_service: separate threads for cry, db, breath
- Split into 3 threads: CryThread, DBThread, BreathThread
- Shared mic buffer accessed from multiple threads


## 2025-07-01 - audio_service threading causing race condition on mic buffer
- Two threads read mic._buf simultaneously
- Partial write during callback = corrupted window
- Fix: use threading.Lock on buffer + Queue for thread communication


## 2025-07-01 - fix race condition: use queue.Queue instead of shared list
- Replaced shared list with collections.deque(maxlen=100) + Lock
- Thread-safe reads confirmed with concurrent stress test


## 2025-07-02 - movenet runs on pi, ~100ms per frame at 192x192 input
- tflite_runtime INT8 model: 95-115ms per inference
- 5fps target = 200ms budget per frame. We use 100ms for inference alone.
- Leaving 100ms for preprocessing + zmq publish


## 2025-07-02 - movenet detecting poses... but its finding my desk chair as a person
- MoveNet detects any human-shape object
- Desk chair + PC monitor = 'torso'
- Must crop to crib ROI before inference


## 2025-07-02 - need to crop to crib region before feeding movenet
- Plan: extract crib bounding box coordinates
- Crop frame to that region
- Upscale to 192x192 for inference


## 2025-07-02 - roi cropping helps, movenet focuses on crib area only
- After ROI crop: no more furniture detections
- Keypoints center on infant/doll only


## 2025-07-02 - visualize keypoints overlaid on frame, save to debug/ folder
- Using cv2.circle to draw keypoints by confidence (green=high, red=low)
- Very helpful to see which keypoints survive from ceiling angle


## 2025-07-02 - add debug/ to gitignore
- Accidentally committed debug/*.jpg test frames
- git rm --cached debug/
- Added debug/ to .gitignore


## 2025-07-03 - pose classification logic: use shoulder-hip angle relative to camera
- Supine: face keypoints visible (conf>0.4) + back keypoints visible
- Prone: face conf < 0.25, back keypoints present
- Side: intermediate, shoulder angle ~45deg


## 2025-07-03 - prone = face keypoints low confidence + back keypoints visible
- Prone rule: nose+eyes+ears all < prone_conf AND shoulder+hip conf > 0.2
- Confidence score: 1.0 - face_conf (higher = more confident prone)


## 2025-07-03 - tested with doll in crib: supine works, prone works, side is garbage
- Supine (face-up): 10/10 detected correctly
- Prone (face-down): 8/10 detected
- Side: 4/10 - shoulder/hip angle ambiguous from top-down camera


## 2025-07-03 - side detection: use hip rotation angle, threshold at 45deg
- Compute left_hip vs right_hip y-coordinate difference
- Large y-diff = body is rotated = side position
- Marginally better: 5/10 now


## 2025-07-03 - vision service captures at 5fps, runs movenet, publishes pose
- Vision service loop: capture -> ROI crop -> upscale -> MoveNet -> classify -> ZMQ
- First full pipeline working end to end


## 2025-07-03 - forgot to close camera on service shutdown, resource leak
- On SIGTERM, camera.stop() not called
- picamera2 holds fd open, next run fails with 'camera already in use'
- Fixed: atexit.register(camera.stop) + try/finally in run()


## 2025-07-03 - vision_service memory usage: ~580MB, within budget
- psutil.Process().memory_info().rss = 580MB
- Budget: 600MB. Acceptable but close.
- Will monitor during soak tests


## 2025-07-03 - add psutil to requirements.txt
- Added psutil==5.9.8 to requirements.txt
- Used for memory monitoring in resource_monitor.py


## 2025-07-05 - respiratory rate from peak counting: values 5-60 bpm lol
- Peak counting method: find_peaks() on optical flow signal
- Peaks detected everywhere because signal is so noisy
- Switching to FFT-based dominant frequency approach


## 2025-07-05 - trying fft instead of peak counting for resp rate
- FFT on 30-second window of optical flow magnitude
- Dominant frequency in 0.15-1Hz range = respiration rate
- Should be more robust than peak counting


## 2025-07-06 - 30-second sliding window for respiratory averaging
- deque(maxlen=150) for 30s at 5fps
- FFT on full window -> dominant freq -> bpm
- Reduces variance compared to 10-second windows


## 2025-07-06 - butterworth bandpass filter 0.15-1.0hz for resp signal
- scipy.signal.butter(2, [0.15, 1.0], btype='band', fs=5)
- Applied before FFT to isolate respiratory frequency range


## 2025-07-06 - but it still jumps +-8 bpm between windows randomly
- Window-to-window variation: 18->26->22->30->20 bpm
- FFT resolution issue: 30 frames = 6 sec, poor freq resolution
- Adding EMA smoothing between windows


## 2025-07-06 - add exponential moving average to smooth between windows
- EMA alpha=0.3: new_bpm = 0.3*raw + 0.7*prev
- Reduces variance but adds responsiveness lag
- Acceptable tradeoff for trend monitoring


## 2025-07-06 - vitals service publishes resp rate to zmq topic vitals/resp
- ZMQ topic: vitals/resp {bpm, confidence, method}
- method='optical_flow', confidence=FFT peak ratio


## 2025-07-06 - vitals service needs pose data from vision service for chest roi
- vitals_service needs keypoints to extract chest ROI
- Cannot import vision_service directly (separate processes)
- Solution: subscribe to vision/pose ZMQ topic


## 2025-07-07 - zmq message protocol: json with mandatory fields topic, ts, data
- Protocol defined in src/utils/zmq_protocol.py
- Mandatory: {topic: str, ts: float, data: dict}
- All services updated to use encode()/decode() helpers


## 2025-07-07 - update env_service to use new zmq protocol
- env_service now uses zmq_protocol.encode() for all publishes
- Subscriber test confirms format compatibility


## 2025-07-07 - update audio_service to use new zmq protocol
- audio_service updated to standard message format
- Existing subscribers still receive messages correctly


## 2025-07-07 - update vision_service to use new zmq protocol
- vision_service: all pub.send() calls use standard format
- Pose, occlusion, motion messages all standardized


## 2025-07-07 - update vitals_service to use new zmq protocol
- vitals_service updated. All 4 services now use same format.
- Ready for alert_engine to subscribe to all


## 2025-07-07 - solution: vitals subscribes to vision/pose and caches latest keypoints
- vitals_service.pose_sub = Subscriber(['vision/pose'])
- poll every frame, cache latest keypoints
- chest_roi extraction uses cached keypoints


## 2025-07-08 - night mode threshold: < 5 lux triggers ir led on + exposure fix
- BH1750 lux < 5.0 -> night mode
- night_mode.py NightModeController class implemented
- Smooth threshold with 1.5s transition buffer


## 2025-07-08 - experiment: histogram equalization on ir frames
- cv2.equalizeHist() on grayscale IR frame
- Global histogram equalization: boosts contrast but also noise


## 2025-07-08 - CLAHE adaptive hist eq works better than global
- cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
- Adaptive per-tile normalization preserves local features better
- MoveNet keypoint confidence improves +12% vs no equalization


## 2025-07-08 - add clahe preprocessing to vision service ir mode path
- vision_service: if night_mode -> CLAHE before MoveNet inference
- Only applied in IR mode (adds 5ms overhead)


## 2025-07-08 - face occlusion: comparing face keypoint visibility scores
- face_conf = mean confidence of [nose, l_eye, r_eye, l_ear, r_ear]
- If face_conf < 0.2 AND body visible -> possible occlusion
- Temporal filter: sustained >3s before flagging


## 2025-07-09 - face occlusion: head turn vs actual blockage distinction
- Head turn: face conf drops but body also rotates (body_conf drops too)
- Occlusion: face conf drops but shoulders/hips remain visible
- body_mean > 0.10 guard added to daytime algorithm


## 2025-07-09 - that helps but not perfect. adding min coverage pct threshold
- 40% of face keypoints must be low-confidence for daytime occlusion
- Not just one keypoint dropping out (e.g. nose clipped at edge)


## 2025-07-09 - face bbox estimation from ear/eye keypoints when partially visible
- If only ears visible, estimate full facial bbox from ear positions
- Helps measure coverage percentage more accurately


## 2025-07-09 - temporal filter: need sustained occlusion >3 seconds
- 3s sustained occlusion before alert (VIS-02 requirement)
- Prevents false alert from baby momentarily covering face with hand


## 2025-07-09 - occlusion detection with temporal filter: way fewer false positives
- Testing with hand-over-face (quick): no alert
- Testing with blanket (sustained): alert fires at exactly 3.1s


## 2025-07-09 - motion classification: still/low/restless from frame diffs
- still: <2% pixels changed per frame (30s avg)
- low: 2-8% pixels changed
- restless: >8% pixels changed


## 2025-07-09 - add motion tracking to vision_service, publishes vision/motion
- vision/motion message: {level, changed_pct, window_avg}
- Published every other frame to save CPU


## 2025-07-10 - refactor: split vision into pose.py, occlusion.py, motion.py, night_mode.py
- pose.py: PoseEstimator class (MoveNet inference)
- occlusion.py: OcclusionDetector class
- motion.py: MotionTracker class
- night_mode.py: NightModeController class


## 2025-07-10 - vision_service.py now just orchestrates submodules
- vision_service.py: 180 lines (down from 400+)
- Each submodule independently testable


## 2025-07-10 - imports fixed, all vision tests pass
- Circular import resolved: Camera not imported in submodules
- Frame passed directly as numpy array to OcclusionDetector, MotionTracker


## 2025-07-10 - add frame counter and fps logging to vision service
- Log FPS every 100 frames
- Frame counter used for alternating occlusion/motion checks


## 2025-07-10 - experiment: skip occlusion check every other frame to save cpu
- Running occlusion every frame: 4.8fps
- Running every other frame: 5.1fps
- Note: occlusion still runs every frame since it's safety-critical (VIS-02)
- Motion tracking alternated instead


## 2025-07-11 - resp absence alert trigger in vitals_service
- If no resp bpm detected for > 15s AND baby still: publish vitals/resp_absence
- Severity: CRITICAL
- Alert engine will fuse with motion data before dispatching


## 2025-07-11 - problem: gross body movement triggers false resp absence
- Baby rolls over = large optical flow spike
- Flow magnitude drops when settling = looks like 'no breathing'
- Need to suppress resp absence alarm during/after gross movement


## 2025-07-11 - distinguish breathing motion from body movement
- Use vision/motion to detect gross body movement
- If motion=restless within last 10s: do not trigger resp absence


## 2025-07-11 - body movement filter: suppress resp alarm if motion level > threshold
- VIT-05 implemented: suppress_resp_alarm if motion=='restless'
- Cooldown 10s after motion stops before monitoring resumes


## 2025-07-11 - add cooldown period after gross movement: wait 10s before monitoring resp
- motion_cooldown_s = 10 seconds after restless motion
- _last_motion_t tracks last restless event
- Only alarm if now - _last_motion_t > 10s AND no bpm for 15s


## 2025-07-12 - alert_engine.py first version: subscribe all zmq topics
- alert_engine subscribes to: audio/cry, audio/dblevel, audio/breath,
  vision/pose, vision/occlusion, vision/motion, vitals/resp, vitals/resp_absence, env/climate


## 2025-07-12 - alert severity enum: INFO / WARN / CRITICAL
- src/alert/severity.py - Severity enum
- src/alert/event.py - AlertEvent dataclass


## 2025-07-12 - alert event data class: type, severity, sensors, confidence, ts
- AlertEvent.to_payload() generates ALT-05 compliant JSON
- Max 512 bytes confirmed


## 2025-07-12 - alert engine v1: just forwards every sensor event as alert
- First version: every ZMQ message -> MQTT alert
- Result: 100+ alerts per minute, completely useless
- Need fusion logic


## 2025-07-12 - obviously that's useless, need fusion logic
- v1 was just a forward relay
- Need to aggregate signals before alerting
- Starting v2: severity mapping per event type


## 2025-07-12 - alert engine v2: severity mapping per event type
- prone -> CRITICAL, temp_high -> WARN, loud_event -> WARN, resp_absence -> CRITICAL
- Still too many alerts but at least severity is meaningful


## 2025-07-12 - still too many alerts, need multi-signal agreement
- Need to require 2+ corroborating signals for CRITICAL
- Single prone detection is not enough without context


## 2025-07-12 - alert engine v3: require 2+ signals for CRITICAL
- Fusion buffer: collect events from all sensors over 10s window
- CRITICAL only if 2 or more sensor types agree
- Prone alone: needs motion=still to confirm it's not a roll


## 2025-07-13 - multi-signal fusion: event buffer with 10-sec sliding window
- Each sensor type has its own deque buffer
- Fusion evaluator checks all buffers against rule set
- Evaluation called every 0.5s from alert_engine loop


## 2025-07-13 - fusion logic: prone alert only if pose=prone AND motion=still
- Rule 1: prone_sustained >= 5s AND motion != restless -> CRITICAL
- Prevents alert during normal baby rolling (arousal from sleep)


## 2025-07-13 - face occlusion CRITICAL only if sustained >5s AND no caregiver
- occ.sustained_s >= 3s (VIS-02 requirement)
- Caregiver suppression: large skeleton in frame


## 2025-07-13 - how to detect caregiver? large skeleton in frame = adult
- If MoveNet detects skeleton much larger than infant baseline = adult in room
- body_size = distance between shoulder and hip keypoints
- Infant baseline: ~50-80px, Adult: >120px at 1.5m distance


## 2025-07-13 - caregiver detection: if any pose skeleton > threshold size = suppress
- Added caregiver_present() check in alert_engine
- If skeleton_size > 120px -> suppress all pose-based CRITICAL alerts
- Hacky but works. Will improve later.


## 2025-07-13 - fusion testing: fewer false criticals but still some edge cases
- Scenario: baby rolling over slowly -> brief prone -> alert
- But this is correct behaviour! rolling into prone IS dangerous
- Need to differentiate: settling in prone vs transitional prone


## 2025-07-13 - log all fusion decisions for debugging
- Added fusion decision logging to alert_engine.log
- Each evaluation cycle logged: events received, rules checked, alerts fired


## 2025-07-12 - alert engine v3: require 2+ signals for CRITICAL
- FusionEngine.evaluate() checks all buffers
- CRITICAL rules require corroborating evidence
- Implemented fusion.py with 5 fusion rules


## 2025-07-14 - false alarm scenario: baby crying + moving = CRITICAL prone??? no
- Bug: cry event + prone event in same 10s window triggered CRITICAL
- Baby crying while rolling is not in danger
- Added: suppress prone if restless AND cry simultaneously


## 2025-07-14 - context rule: crying + moving = baby awake = suppress prone alert
- Rule added to FusionEngine: if motion=restless AND cry_detected in buffer -> suppress prone CRITICAL
- Baby actively crying = definitely not dangerously prone-and-still


## 2025-07-14 - context rule: tv noise = suppress db alert, check frequency spectrum
- First thought: spectral analysis to detect TV vs real noise
- Actually too complex. Just increase sustained duration.


## 2025-07-14 - actually spectral analysis is overkill, just increase sustained duration
- TV tends to vary in volume (ads, quiet scenes)
- Real sustained noise (vacuum cleaner, alarm) stays constant >5s
- Increased db alert requirement from 3s to 5s sustained


## 2025-07-14 - false alarm filter config in yaml: rules as config not code
- config/alert_rules.yaml: threshold values, suppression conditions
- alert_engine loads rules on start + hot-reload on config change


## 2025-07-14 - alert rules yaml schema: conditions, suppressions, thresholds
- alert_rules.yaml: each rule has threshold, suppress conditions, rate_limit
- FusionEngine reads from config.get('rules')


## 2025-07-14 - alert engine reads rules from yaml on startup
- FusionEngine.__init__ reads cfg['rules'] for all tunable parameters
- No hardcoded values except defaults


## 2025-07-14 - forgot to add yaml parsing for nested rules, fixing
- config_loader.get('rules','prone','min_sustained_s') was returning None
- Dict nested properly in YAML but get() only 2 levels deep
- Fixed: use cfg['rules']['prone']['min_sustained_s'] with .get()


## 2025-07-14 - alert payload format: json with all required fields per ALT-05
- AlertEvent.to_payload(): ts, type, severity, sensors[], confidence, value, message
- Max payload size: 347 bytes (tested with longest possible values)


## 2025-07-14 - payload size check: max 347 bytes, well under 512 limit
- json.dumps(event.to_payload()) -> 347 bytes worst case
- Well within ALT-05: 512 bytes max


## 2025-07-15 - install mosquitto mqtt broker
- sudo apt install mosquitto mosquitto-clients
- Default config: port 1883 no TLS


## 2025-07-15 - generate self-signed tls certs for mqtt
- scripts/generate_certs.sh: openssl req to generate CA + server cert
- Stored in config/certs/ (gitignored)


## 2025-07-15 - mosquitto config with tls, port 8883
- config/mosquitto.conf: TLS on port 8883
- sudo mosquitto -c config/mosquitto.conf


## 2025-07-15 - mqtt publish from python: paho-mqtt client
- pip install paho-mqtt==2.0.0
- Test script: connect, publish 'hello', subscribe on another terminal


## 2025-07-15 - alert engine publishes to mqtt topic edgewatch/alert/#
- Topics: edgewatch/alert/critical, edgewatch/alert/warn, edgewatch/alert/info
- Retain=True so late subscribers get last alert


## 2025-07-15 - mqtt test subscriber receives alerts from alert engine!
- First end-to-end test! sensor -> zmq -> alert_engine -> mqtt -> subscriber
- Alert received in 5.8 seconds from event trigger


## 2025-07-15 - mqtt disconnecting after ~30 seconds randomly
- mosquitto logs: 'Client disconnected: keepalive timeout'
- Default keepalive is 15s, Python client not sending PINGREQ fast enough


## 2025-07-15 - mosquitto log: client exceeded keepalive timeout
- mosquitto.conf keepalive_interval too short
- paho client keepalive: default 60s
- Mismatch: broker expects ping within 15s, client sends at 60s


## 2025-07-15 - increase keepalive to 120s in mosquitto config
- keepalive_interval = 120 seconds in mosquitto.conf
- paho client: mqtt.Client(keepalive=120)


## 2025-07-15 - also increase max_connections from 10 to 100
- Default max_connections=10 in older mosquitto versions
- Set to 100 to allow app + multiple test clients simultaneously


## 2025-07-15 - mqtt stable now, tested for 15 min no disconnects
- 15 minute continuous MQTT session: 0 disconnections
- 900 alert messages published, all received by subscriber


## 2025-07-16 - session_manager.py: auto-detect sleep start and end
- session_manager.py implements SES-01
- Subscribes to vision/motion, audio/cry, env/climate


## 2025-07-16 - sleep start: motion=still + no cry for >5min
- STILL_THRESHOLD_S = 300 seconds (5 minutes)
- Both motion=still AND no cry detected in that window


## 2025-07-16 - sleep end: sustained motion + cry detected
- End condition: restless motion for >1min OR cry detected during session
- For now: manual session end from parent app as fallback

