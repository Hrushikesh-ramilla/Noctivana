
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


## 2025-07-16 - session state machine: IDLE -> MONITORING -> ENDED
- Three states: IDLE (waiting), MONITORING (active session), ENDED (export on stop)
- State transitions logged to devlog


## 2025-07-16 - sqlite schema for session logs
- Tables: sessions, alerts, env_readings
- sessions: id, start_ts, end_ts, alert_count
- alerts: session_id, ts, type, severity, value, message


## 2025-07-16 - add sqlcipher encryption... and it breaks everything
- pip install pysqlcipher3 -> compilation error
- Missing: libssl-dev libsqlite3-dev on Pi
- pysqlcipher3 needs to compile native extension


## 2025-07-16 - sqlcipher python bindings wont compile on arm64
- aarch64 platform not tested well by pysqlcipher3
- CFLAGS needed: -DSQLITE_HAS_CODEC -DSQLITE_TEMP_STORE=2
- Going to try building from source


## 2025-07-17 - use pysqlcipher3 instead, finally compiles
- sudo apt install libssl-dev libsqlite3-dev
- CFLAGS='-DSQLITE_HAS_CODEC' pip install pysqlcipher3
- Took 3 hours total


## 2025-07-17 - session logging works, encrypted db confirmed with hex dump
- hexdump sessions.db | head -> SQLite header NOT visible (encrypted!)
- With correct key: SELECT * FROM sessions -> rows visible
- NFR-S2 confirmed


## 2025-07-18 - ble_service.py skeleton using bluez/dbus
- src/services/ble_service.py created
- Using bluezero library (wraps BlueZ D-Bus API)
- pip install bluezero


## 2025-07-18 - reading bluez documentation... this is painful
- BlueZ D-Bus API has minimal Python docs
- bluezero is better but also sparse
- Looking at example peripheral code


## 2025-07-18 - gatt service definition: edgewatch alert characteristic
- Service UUID: 12345678-1234-1234-1234-1234567890AB (random 128-bit)
- Alert characteristic: ...AC
- Flags: notify + read


## 2025-07-18 - ble advertisement registered but phone cant find it
- bluezero peripheral.publish() called
- nRF Connect on Android: no EdgeWatch device visible
- Missing something in advertisement data


## 2025-07-18 - missing service UUID in advertisement data
- Advertisement packet must include service_uuids to be discoverable
- Added service_uuid to advertising data explicitly


## 2025-07-18 - fix advertisement: add UUID and local name EdgeWatch
- Added local_name='EdgeWatch' to Peripheral constructor
- Added service UUID to manufacturer data
- Phone can now see EdgeWatch in scan


## 2025-07-18 - phone discovers EdgeWatch!! connecting...
- nRF Connect: discovered EdgeWatch BLE device
- Connected successfully
- Service and characteristic visible


## 2025-07-18 - gatt read works, notification works, android confirmed
- Read characteristic: returns current timestamp
- Enable notification: Pi sends 'test' payload
- Android nRF Connect receives notification


## 2025-07-18 - ble service subscribes to alert engine, forwards CRITICAL via notify
- BLE service subscribes to alert/trigger ZMQ topic
- On CRITICAL/WARN severity: notify connected BLE client
- If not connected: queue for delivery on reconnect (ALT-04)


## 2025-07-19 - first full integration test: start ALL services simultaneously
- Starting: zmq_proxy, env, audio, vision, vitals, alert_engine, session, ble
- All services launched via supervisor.py


## 2025-07-19 - immediate crash: zmq address already in use on port 5555
- Multiple services binding PUB socket on same port = EADDRINUSE
- Need a single XPUB/XSUB proxy that all services connect to


## 2025-07-19 - multiple publishers binding same port = conflict
- ZMQ bind() can only be called once per address
- Each service must connect() not bind()
- Need a proxy process that does bind()


## 2025-07-19 - zmq architecture fix: one XPUB/XSUB proxy, services connect not bind
- zmq_proxy.py: binds XPUB (5555) and XSUB (5556)
- All services: Publisher connects to port 5556, Subscriber to 5555


## 2025-07-19 - add zmq proxy process: src/services/zmq_proxy.py
- zmq_proxy.py runs as separate process
- Must start before all other services


## 2025-07-19 - update all services to connect to proxy instead of binding
- Updated zmq_bus.py Publisher to connect to SUB_ADDR (5556)
- Updated zmq_bus.py Subscriber to connect to PUB_ADDR (5555)


## 2025-07-19 - integration test #2: services start without port conflict
- All 8 services start cleanly
- ZMQ messages flowing through proxy
- Progress!


## 2025-07-19 - but vision service crashes after 3 min with OOM
- Crash: MemoryError in numpy during optical flow
- psutil shows vision_service RAM at 1.5GB (!)
- Memory leak: OpenCV frames accumulating


## 2025-07-19 - opencv frames accumulating, numpy arrays not freed
- frame variable reassigned each loop but old numpy arrays held in scope
- Python GC doesn't immediately collect large numpy arrays
- Need explicit del + gc.collect()


## 2025-07-19 - fix: explicitly del frame + gc.collect() every 100 frames
- Added: del frame, crop, upscaled at end of loop
- gc.collect() every 100 frames
- Memory stable at 620MB after fix


## 2025-07-20 - integration test #3: runs 12 min then audio service hangs
- Audio service stopped responding after 12 min
- No crash, just hung - buffer growing unbounded
- collections.deque maxlen not set


## 2025-07-20 - fix audio: replace growing list with collections.deque(maxlen=50)
- Audio inference buffer was plain list(), grew to 50k items
- Changed to deque(maxlen=50) = keep last 50 windows
- Memory stays bounded


## 2025-07-20 - integration test #4: 30 min stable!! all services running
- 30 minute continuous run: 0 crashes
- RAM: 1.7GB total across all services
- CPU: 65%
- Temp: 58C


## 2025-07-20 - add resource monitor script: logs cpu, ram, temp per service
- scripts/monitor_resources.py: psutil per-process stats
- Logs every 60s: cpu%, mem_rss, pi_temp


## 2025-07-20 - add process supervisor script, restarts crashed services
- scripts/supervisor.py: subprocess.Popen for each service
- Polling every 10s
- Restarts crashed services with 3s delay


## 2025-07-20 - supervisor uses subprocess + signal handling
- SIGTERM -> terminate all child processes cleanly
- Each service has startup delay to avoid boot race conditions


## 2025-07-20 - systemd unit files for all services
- systemd/edgewatch-*.service for each service
- Restart=always + RestartSec=5 for auto-recovery (NFR-R2)


## 2025-07-20 - systemd ordering: zmq_proxy first, then sensors, then alert
- After=edgewatch-zmq-proxy.service for all dependent services
- Requires= directive ensures proper startup order


## 2025-07-21 - prone detection mannequin test: 7/10 detections
- Test setup: mannequin doll, ceiling mount at 1.5m
- 10 prone placements, 7 triggered alert
- Target: 9/10


## 2025-07-21 - movenet confidence very low on small doll from 1.5m ceiling height
- At 1.5m the doll is ~60x40px in 640x480 frame
- MoveNet input is 192x192 - doll is tiny fraction of it
- Need to upscale crib crop before inference


## 2025-07-21 - experiment: crop crib roi then upscale to 256x256 before movenet
- Extract crib_roi (say 200x150px), upscale to 256x256 with INTER_LINEAR
- Feed this to MoveNet instead of downscaled full frame


## 2025-07-21 - upscaled roi: movenet keypoint confidence up ~20%
- Average keypoint confidence: 0.45 -> 0.67
- Nose confidence in prone: 0.08 -> 0.12 (still low but better)


## 2025-07-21 - but upscale resize adds 50ms per frame, fps drops to 4.2
- INTER_CUBIC resize: +70ms, fps=3.8
- INTER_LINEAR resize: +50ms, fps=4.2
- Below 5fps target (NFR-P2)


## 2025-07-21 - use cv2.INTER_LINEAR instead of INTER_CUBIC for resize, saves 15ms
- Switched from INTER_CUBIC to INTER_LINEAR for ROI upscale
- Quality difference minimal at this small scale


## 2025-07-21 - skip motion analysis every other frame, focus cpu on pose
- Motion tracking runs every other frame (frame_n % 2)
- Occlusion remains every frame (safety critical)
- FPS: 5.1fps achieved


## 2025-07-21 - prone detection with upscaled roi: 9/10 mannequin tests!!
- Retest with 256x256 upscaled ROI inference: 9/10 prone detections
- VIS-01 acceptance criteria MET!


## 2025-07-21 - lower prone confidence threshold from 0.5 to 0.3 for safety margin
- Conservative threshold per SRS: trigger at 25% prone confidence
- Using 0.25 in config (prone_confidence: 0.25)
- Higher sensitivity = some false positives but safer


## 2025-07-21 - latency measurement: event to alert in 5.8 seconds average
- Measured: camera event -> ZMQ -> fusion -> MQTT publish
- Average: 5.8s, 95th percentile: 7.2s
- Under 8s target (NFR-P1)


## 2025-07-21 - document latency breakdown in docs/latency.md
- Breakdown: capture 200ms, inference 150ms, zmq 20ms, fusion 100ms, mqtt 80ms, network 200ms
- Total ~750ms for Pi, network/app adds the rest


## 2025-07-22 - low power mode: reduce to 2fps when baby still for >5min
- NFR-P4: low-power monitoring when baby still
- _enter_low_power(): camera.set_fps(2), pause rPPG


## 2025-07-22 - low power pauses rppg and reduces vision processing
- In low power: vitals_service skips rPPG (~20% CPU saving)
- vision_service at 2fps: ~15% CPU saving


## 2025-07-22 - wake from low power on any motion or cry event
- vision/motion level != still -> _exit_low_power()
- audio/cry detected -> alert engine wakes sensors


## 2025-07-22 - low power saves ~25% cpu, temp drops 8C
- Normal: 65% CPU, 58C
- Low power (2fps): 40% CPU, 50C
- Significant thermal and performance improvement


## 2025-07-22 - problem: low power -> full wake takes 1.5s, blanket in that window?
- Camera set_fps(2) -> lag to first 5fps frame ~1.5s
- Could miss face occlusion event starting during this window


## 2025-07-22 - solution: always run occlusion check even in low power (at 2fps)
- Occlusion check runs every frame regardless of low-power state
- Only motion tracking and rPPG are reduced
- Safety-critical features always at full rate


## 2025-07-22 - startup self-test: check camera, mic, i2c sensors, report status
- NFR-R3: self-test on startup
- Each service publishes self-test result to zmq startup/selftest


## 2025-07-22 - self-test publishes results to zmq + logs to file
- SelfTest results: {camera: ok/fail, mic: ok/fail, scd40: ok/fail, ...}
- Published to startup/selftest ZMQ topic
- Alert engine reads it, issues WARN if any critical sensor missing


## 2025-07-22 - self-test warns if any critical sensor missing
- If camera=fail: WARN alert + LED amber on startup
- If mic=fail: WARN alert (non-critical)
- If all=ok: LED green, ready


## 2025-07-23 - rppg attempt #1: extract green channel from face ROI
- Green channel: best photoplethysmographic signal in skin
- Extract face region using upper-center of frame
- Compute mean green value per frame


## 2025-07-23 - rppg theory: subtle green channel variation = pulse
- Blood absorption peak around 550nm (green light)
- As heart pumps: skin blood volume changes slightly
- Camera detects this as tiny green channel oscillation


## 2025-07-23 - rppg from ceiling camera: face is literally 20x30 pixels
- At 1.5m ceiling: infant face region ~20x20px in 640x480 frame
- Even after upscale: only interpolated pixels
- Signal-to-noise ratio is terrible


## 2025-07-23 - upscale face roi for rppg? interpolation adds noise
- Tried: upscale face ROI to 64x64 before green extraction
- Interpolation adds structured noise that mimics pulse signal
- Makes results worse not better


## 2025-07-23 - rppg readings: 45, 120, 89, 200, 33... this is noise
- Consecutive readings: 45->120->89->200->33 bpm
- Physiologically impossible variation
- This is random noise in the FFT output


## 2025-07-23 - try temporal bandpass filter on green channel signal
- Butterworth bandpass 0.8-3.0Hz (48-180 bpm)
- Applied to 10-second green channel history


## 2025-07-23 - rppg with filter: values hover 60-150 range, very unstable
- After filtering: 60->145->78->102->95 bpm
- Better range but still physiologically implausible variation
- Fundamental problem: signal too weak at ceiling distance


## 2025-07-23 - add face tracking ema for roi stabilization
- EMA smoothing on face ROI position: prevents ROI jumping
- Reduces noise from ROI misalignment
- Marginal improvement only


## 2025-07-23 - rppg marginally better but fundamentally unreliable at this distance
- Decision: accept rPPG as experimental/POC
- Clearly labeled 'experimental' in app and payload
- Will not use for any safety-critical fusion rules


## 2025-07-23 - mark rppg as experimental, add disclaimer in zmq payload
- experimental: True field in all rPPG payloads
- Confidence capped at 0.5 maximum
- App shows disclaimer: 'Experimental - accuracy not guaranteed'


## 2025-07-24 - rppg: only enable when baby face-up + still + good lighting
- Conditional: run rPPG only when pose=supine AND motion=still AND lux>50
- Reduces garbage readings from non-ideal conditions


## 2025-07-24 - rppg publishes to vitals/rppg with experimental flag
- vitals/rppg: {bpm, confidence, experimental: True}
- Alert engine ignores rPPG for fusion rules
- App shows as 'indicative only'


## 2025-07-24 - revisit resp rate: test with metronome-controlled breathing sim
- Built mechanical breathing sim: small motor + balloon on metronome
- Set to 30 bpm, measure optical flow output
- More controlled than previous ad-hoc tests


## 2025-07-24 - resp rate vs reference: +-6 bpm in 70% of windows
- Regression from 78%! Optical flow params changed during refactor
- Farneback poly_n was changed from 7 to 5 (less accurate)


## 2025-07-24 - optical flow params were changed during refactor, oops
- Found the culprit: FB_PARAMS poly_n=5 (changed from 7 to save CPU)
- Restoring to poly_n=7


## 2025-07-24 - resp rate back to +-5 bpm in 78% of windows
- After restoring poly_n=7: ±5 bpm in 78% windows
- Better but still not at ±4 in 80% target
- Need to tune window_size parameter next


## 2025-07-24 - increase averaging window from 30s to 45s
- deque maxlen: 150->225 (45s at 5fps)
- Longer FFT window = better frequency resolution
- Trade-off: slower response to rate changes


## 2025-07-24 - resp rate with 45s window: +-4.5 bpm in 79%
- So close!! 79% vs 80% target
- Need to tune one more parameter
- Trying window_size in Farneback (spatial smoothing)


## 2025-07-25 - auto ir mode complete: bh1750 < 5 lux triggers everything
- VIS-03 complete: BH1750 -> NightModeController -> IR LED + camera exposure
- Transition buffer (1.5s) prevents false alerts during switch


## 2025-07-25 - ir led brightness control via pwm, not just on/off
- PWM duty cycle: 100% for full darkness, 50% for dim conditions
- Smoother transition at light/dark boundary


## 2025-07-25 - ir mode transition takes 2 seconds, camera needs to readjust
- Camera auto-exposure needs 2s to settle after switching to manual
- During this time: frames are over/under-exposed


## 2025-07-25 - buffer 1.5s of last-known state during ir transition
- NightModeController.in_transition(): True for 1.5s after mode switch
- Alert engine: suppress position/occlusion alerts during transition


## 2025-07-25 - env_service: add logging to csv file per session
- ENV-05: real-time data + local CSV logging
- CSV: timestamp, temp_c, humidity, co2_ppm, tvoc_ppb, lux
- One CSV per session


## 2025-07-25 - csv format: timestamp, temp, humidity, co2, voc, lux, db_spl
- Added db_spl column from audio_service logging
- ENV-04: ambient sound level at 1-second resolution


## 2025-07-25 - sgp30 returns 0 randomly after long running, not just boot
- After 2+ hours: sgp30.read() occasionally returns (0, 400)
- Not just boot-time issue
- Suspected: sensor baseline drift or I2C timing issue


## 2025-07-25 - workaround: if sgp30 reads 0, use last known value, log warning
- SGP30.read() now maintains _tvoc, _eco2 last-known-good
- Zero reads: return last-known + log WARNING
- Prevents false 'clean air' readings after sensor glitch


## 2025-08-01 - overnight test prep: checklist of what to verify
- Test checklist: all services start, mqtt connects, ble advertises
- Monitor: RAM < 2.5GB, temp < 80C, no crashes


## 2025-08-01 - add watchdog timer in supervisor: restart if service unresponsive 30s
- Each service sends heartbeat to supervisor every 10s
- Supervisor restarts service if heartbeat absent for 30s
- NFR-R2 implementation complete


## 2025-08-01 - all services report heartbeat to supervisor every 10s
- Added heartbeat thread to each service
- Heartbeat: touch a PID file every 10s
- Supervisor checks file mtime to verify liveness


## 2025-08-01 - privacy mode: mqtt command disables camera + mic services
- NFR-S5: MQTT topic edgewatch/command/privacy {enable: true/false}
- alert_engine receives command, sends SIGSTOP to vision + audio services


## 2025-08-01 - privacy mode leaves env + radar (if present) running
- Only camera (vision_service) and mic (audio_service) paused
- env_service + ble_service continue in privacy mode
- Status LED blinks purple in privacy mode


## 2025-08-01 - visual indicator: status led blinks purple in privacy mode
- Added 'privacy' state to StatusLED: purple (128,0,128)
- Blinks at 0.5Hz to indicate active privacy mode


## 2025-08-01 - overnight test #1: everything starts, logging begins...
- t=0: all services started via supervisor
- t=10min: all stable, RAM=1.7GB, temp=55C
- Letting it run overnight...


## 2025-08-01 - fix: forgot to increase mosquitto logging before overnight test
- mosquitto.conf: log_type all
- Need verbose logs to diagnose any overnight issues


## 2025-08-01 - checked at 10pm: 4 hours running, vision service using 1.2GB ram?!
- psutil check: vision_service RSS = 1.2GB (was 620MB at start)
- Memory growing ~150MB/hour
- Leak must be in something we fixed earlier but re-introduced


## 2025-08-01 - overnight test #1 FAILED: vision OOM at ~4.5 hours
- Crash at t~4.5hrs: MemoryError in numpy
- vision_service RSS was 1.8GB before crash
- Need to find the leak - new one since last fix


## 2025-08-02 - vision memory leak investigation: frame references held by occlusion history
- Found it: OcclusionDetector._conf_hist stores deque of numpy arrays
- Was using deque(maxlen=20) of FULL FRAMES not just keypoints
- 20 * 640*480*3 bytes = 18MB per deque * some multiplier = huge


## 2025-08-02 - fix: occlusion history stores only keypoint data, not full frames
- Changed: _conf_hist stores only (face_conf, body_conf) floats
- Not the full numpy frame array
- Memory drops immediately: 1.2GB -> 640MB


## 2025-08-02 - also: numpy array copies in motion tracker were not freed
- MotionTracker._history: deque of np.ndarray copies of frames
- Changed: store only the changed_pct float
- Another ~200MB freed


## 2025-08-02 - vision service memory: stable at ~620MB over 2hr test
- 2hr soak test: vision_service stable at 620MB +-10MB
- No growth trend - leak fixed!


## 2025-08-02 - audio service: fixed similar issue with mfcc feature history
- audio_service was keeping last 100 MFCC arrays in history
- Each MFCC: (40, 40) float32 = 6.4KB * 100 = 640KB -- actually small
- But also keeping raw audio windows: 15360 * 4 bytes each
- Fixed: keep only classification results, not raw windows


## 2025-08-02 - init react native expo app
- npx create-expo-app edgewatch-app (inside app/)
- Bare workflow, TypeScript config
- Bottom tab navigation


## 2025-08-02 - expo template, typescript config
- Using JS not TS for simplicity
- Expo SDK 51


## 2025-08-02 - add .gitignore for node_modules inside app/
- app/.gitignore: node_modules/, .expo/, android/build/
- Not committing 200MB of npm packages


## 2025-08-02 - npm install react-native-mqtt paho-mqtt.js
- react-native-mqtt for MQTT client in RN
- paho-mqtt as fallback


## 2025-08-02 - mqtt connection to pi broker from react native
- app/src/services/mqtt.js: MqttProvider context
- Connects to mqtt://edgewatch.local:8883
- Subscribes to edgewatch/alert/#


## 2025-08-02 - basic mqtt subscribe: receiving alert messages on phone!
- First app milestone! Phone receives WARN alert from Pi
- JSON payload displayed in console log
- Time to build the UI


## 2025-08-03 - app: alerts screen skeleton
- AlertsScreen.js: FlatList of AlertCard components
- Most recent alert at top


## 2025-08-03 - alert card component: severity icon + message + timestamp
- AlertCard: colored left border (red/orange/gray) by severity
- Shows type, message, timestamp


## 2025-08-03 - severity colors: red=critical, orange=warn, gray=info
- CRITICAL: #ef4444, WARN: #f59e0b, INFO: #6b7280


## 2025-08-03 - alerts screen: flatlist of alert cards, most recent first
- setAlerts(prev => [payload, ...prev].slice(0, 100))
- Keep max 100 alerts in memory


## 2025-08-03 - app styling: dark theme, deep navy background
- backgroundColor: #0d1117 (GitHub dark)
- Card: #161b22
- Accent: #7c3aed (purple)


## 2025-08-03 - app typography: using system fonts, clean and readable
- System font stack for now (no custom fonts)
- Clear hierarchy: severity (small) -> type (bold) -> message


## 2025-08-03 - critical alert: full-screen red overlay with vibration
- TODO: implement full-screen CRITICAL alert overlay
- For now: loud sound + vibration via Vibration.vibrate([0,500,200,500])


## 2025-08-03 - session history screen: list of past sessions
- SessionScreen: shows current session summary
- Alert counts, duration, env summary


## 2025-08-03 - session data from mqtt retained messages
- MQTT retain=True on edgewatch/alert/* topics
- App gets last state immediately on connect
- Not ideal but works without direct DB access


## 2025-08-03 - session detail: alert count, duration, env summary
- Shows: critical count, warn count, total events
- Duration from first to last alert timestamp


## 2025-08-03 - app navigation: bottom tab bar for alerts/sessions/settings
- Bottom tab navigator: Alerts / Sessions / Settings / Setup
- Dark tab bar matching overall theme


## 2025-08-03 - navigation styling: clean icons, active tab highlight
- Active: #7c3aed, Inactive: #6b7280
- No icons yet (using text labels for now)


## 2025-08-04 - settings screen: threshold configuration sliders
- SettingsScreen: sliders for temp_high, db_threshold
- Privacy mode toggle switch


## 2025-08-04 - temp high/low threshold, humidity range, cry sensitivity
- Temp slider: 20-35C range, step 0.5
- dB slider: 50-90 dB range, step 1


## 2025-08-04 - db threshold slider, default 70db
- Default 70dB as per SRS AUD-03
- NFR-U3: user-adjustable thresholds


## 2025-08-04 - settings values stored in asyncstorage locally
- @react-native-async-storage/async-storage
- Persists across app restarts
- Syncs to device on each change


## 2025-08-04 - settings -> mqtt publish to edgewatch/config topic
- client.publish('edgewatch/config', JSON.stringify({tempHigh: 28.5}))
- Pi alert_engine subscribes and updates thresholds live


## 2025-08-04 - config subscriber on pi: reads mqtt config, updates config.yaml
- Added config subscriber thread in alert_engine
- Receives config updates, patches config.yaml
- watchdog triggers hot-reload in all services


## 2025-08-04 - hot config reload: services watch config file for changes
- watchdog library: FileSystemEventHandler on config.yaml
- On change: Config.reload()
- All services use Config.get() -> auto-picks up new values


## 2025-08-04 - config reload uses file watcher (watchdog library)
- watchdog.observers.Observer() monitors config/ directory
- FileModifiedEvent -> Config.reload()


## 2025-08-04 - privacy mode toggle in settings
- Switch component in SettingsScreen
- Publishes {privacy: true/false} to edgewatch/config


## 2025-08-04 - privacy mode sends mqtt command, pi disables camera+mic
- alert_engine receives privacy command
- Sends SIGSTOP to vision_service + audio_service PIDs
- SIGCONT to re-enable


## 2025-08-04 - status banner component: shows connection state
- StatusBanner: green when MQTT connected, red when disconnected
- Fixed at top of AlertsScreen


## 2025-08-05 - ble pairing flow in app: setup wizard
- SetupScreen: 3-step wizard
- Step 1: scan for EdgeWatch BLE
- Step 2: connect + pair
- Step 3: verify + done


## 2025-08-05 - npm install react-native-ble-plx for ble in rn
- react-native-ble-plx@2.0.3 installed
- Requires Android permissions: BLUETOOTH_SCAN, BLUETOOTH_CONNECT


## 2025-08-05 - ble scan for edgewatch device, show in list
- BleManager.startDeviceScan(null, null, callback)
- Filter: deviceName == 'EdgeWatch'


## 2025-08-05 - 3-step wizard: scan -> select -> pair -> verify
- Step 0 -> 1: scan finds EdgeWatch
- Step 1 -> 2: connect + discover services
- Step 2: verified, monitoring active


## 2025-08-05 - ble pairing works on pixel 7, connected!
- Pixel 7 Android 14: scan works, connect works, notification received


## 2025-08-05 - ble crash on samsung a52: BluetoothAdapter is null
- Samsung A52 Android 12: crash on BleManager init
- 'BluetoothAdapter is null' -> react-native-ble-plx version issue


## 2025-08-05 - react-native-ble-plx version incompatibility with expo
- Latest version (3.x) breaks with Expo SDK 51
- Need specific version 2.0.3


## 2025-08-05 - downgrade ble-plx to 2.0.3, samsung crash fixed
- npm install react-native-ble-plx@2.0.3
- Samsung crash gone. Pixel 7 still works.


## 2025-08-05 - ble fallback: if wifi mqtt fails, switch to ble alerts
- App monitors MQTT connection state
- On disconnect: fall back to BLE notifications
- ALT-04: no missed CRITICAL alerts


## 2025-08-05 - app build: expo run:android, generates debug apk
- expo run:android builds debug APK
- Installed on Pixel 7 directly
- Full app flow tested on real device


## 2025-08-06 - overnight test #2: started at 11pm last night
- Started all services at 23:00
- Monitoring remotely...


## 2025-08-06 - result: ran 7 hours then vision service segfault
- t=7hr: vision_service terminated with SIGSEGV
- supervisor restarted it but session log shows gap
- Core dump: crash in cv2.cvtColor


## 2025-08-06 - segfault in cv2.cvtColor when camera returns corrupt frame
- Crash happens at 06:00 local time = Pi starts thermal throttling
- When throttling: picamera2 drops frames -> returns None or corrupt
- cv2.cvtColor(None) = SIGSEGV (no null check in C extension)


## 2025-08-06 - add try/except around ALL opencv calls in vision pipeline
- Wrapped every cv2.* call in try/except Exception
- On exception: log warning, skip frame, continue loop


## 2025-08-06 - camera sometimes returns None frame after thermal throttle
- picamera2 can return None when camera drops frame under thermal stress
- Must check `if frame is None` before any processing


## 2025-08-06 - fix: skip None frames with warning log, continue loop
- Added: if frame is None: logger.warning('Null frame skipped'); continue
- Also check: if frame.size == 0: skip


## 2025-08-06 - add frame validity check: shape, dtype, not-all-zeros
- Full check: frame is not None AND frame.size > 0 AND frame.shape[2]==3
- Belt-and-suspenders approach for all OpenCV inputs


## 2025-08-06 - thermal monitoring: read cpu temp from sysfs
- /sys/class/thermal/thermal_zone0/temp: Pi CPU temperature in milli-C
- 72000 = 72°C
- Added src/utils/thermal.py


## 2025-08-06 - log cpu temp every 60s, warn at 70C, alert at 80C
- alert_engine logs cpu temp every 60s via thermal.check_thermal()
- WARN alert if temp > 70C
- CRITICAL shutdown-sequence if temp > 80C (safety)


## 2025-08-06 - if temp > 75C: reduce to 3fps, pause rppg
- Proactive thermal throttling before kernel throttles
- At 75C: call camera.set_fps(3), skip rPPG
- Prevents SIGSEGV from frame corruption


## 2025-08-06 - overnight test #3 starting now with heatsink attached
- Attached aluminum heatsink + thermal paste to Pi CPU
- Starting test at 20:00
- Will check at midnight and 6am


## 2025-08-06 - 4.5 hours in, stable, temp 64C, ram 1.8GB
- t=4.5hrs: 0 crashes, temp 64C (vs 72C without heatsink), RAM stable
- Heatsink is making a real difference


## 2025-08-07 - overnight test #3 PASSED: 10 hours!! no crash, max temp 72C
- 10 hours continuous: 0 crashes!
- Max temp: 72C (at hour 8, heatsink saturated)
- RAM: 1.8GB stable throughout
- 4 WARN alerts, 0 false CRITICAL


## 2025-08-07 - overnight test log: 4 WARN alerts (temp fluctuation), 0 false CRITICAL
- WARN alerts: temp_high at 3am (room heated up slightly)
- 0 false CRITICAL: fusion rules working correctly
- NFR-R1: 10hr uptime confirmed


## 2025-08-07 - mannequin prone detection retest: preparing test rig
- Standard infant mannequin doll
- Ceiling mount at 1.5m above
- 10 test scenarios: prone from different angles


## 2025-08-07 - prone test: 10 scenarios - position baby, check alert
- Scenario 1-5: straight prone (face-down)
- Scenario 6-8: angled prone (45 degrees)
- Scenario 9-10: prone near edge of crib


## 2025-08-07 - prone result: 8/10 at default threshold
- 8/10: miss #9 (near crib edge, keypoints partially out of ROI)
- Miss #10: angled prone at 60 degrees (side-prone boundary)
- Lowering confidence threshold from 0.30 to 0.25


## 2025-08-07 - lower confidence threshold from 0.30 to 0.25
- config/config.yaml: prone_confidence: 0.25
- More sensitive = may increase false positives slightly
- Safety requirement: better to over-alert than miss


## 2025-08-07 - prone result after adjustment: 9/10
- 9/10 with prone_confidence=0.25!
- VIS-01 acceptance criteria MET
- Miss was scenario #10: extreme angle (body almost horizontal)


## 2025-08-07 - face occlusion test: blanket over doll face, 10 trials
- Using thin muslin blanket (realistic infant blanket)
- Placing over face in 10 different ways
- Measuring time to alert detection


## 2025-08-07 - occlusion daytime: 9/10, IR mode: 6/10
- Daytime (lights on): 9/10 detected, avg 3.8s
- IR mode (lights off): 6/10 detected
- IR mode dramatically worse


## 2025-08-07 - IR occlusion: keypoint dropout approach instead of bbox coverage
- Daytime algorithm: coverage_pct based
- IR algorithm: ALL face keypoints < 0.1 AND body visible
- More aggressive for IR since contrast is lower


## 2025-08-07 - IR algorithm: if ALL face keypoints < 0.1 confidence + body visible = occluded
- Updated occlusion.py night_mode branch
- np.all(face_confs < 0.1) AND body_mean > 0.15


## 2025-08-07 - IR occlusion retest: 8/10
- After IR algorithm update: 8/10 detected in IR mode
- Improvement from 6/10 to 8/10
- Just meets acceptance criteria (marginal)


## 2025-08-07 - daytime occlusion still 9/10 with new algorithm
- Confirmed: daytime algorithm unchanged, still 9/10
- No regression from IR algorithm change


## 2025-08-07 - document all test results in docs/test_results.md
- docs/test_results.md: all acceptance criteria test outcomes
- VIS-01: 9/10 PASS, VIS-02 day: 9/10 PASS, VIS-02 IR: 8/10 MARGINAL


## 2025-08-08 - respiratory rate test: mechanical breathing sim with metronome
- Mechanical rig: small DC motor + balloon on metronome beat
- Simulates chest rise at controlled rates
- Test rates: 20, 30, 40 bpm


## 2025-08-08 - set metronome at 30 bpm, measure optical flow output
- Reference: 30 bpm mechanical
- 10 consecutive 30s windows measured
- Optical flow output vs reference


## 2025-08-08 - result: +-4 bpm in 75% of 30s windows
- At 30 bpm: 75% of windows within ±4 bpm
- Target: 80%
- Need to tune Farneback window_size parameter


## 2025-08-08 - try: increase pyr_scale in farneback from 0.5 to 0.3
- pyr_scale: controls pyramid scaling (0.5 = half-size each level)
- Smaller pyr_scale = finer detail at expense of large motion


## 2025-08-08 - worse. revert.
- pyr_scale=0.3 gave worse results: 70% within ±4
- Reverted to 0.5. Moving to poly_n.


## 2025-08-08 - try: increase polynomial expansion (poly_n from 5 to 7)
- poly_n=7: larger neighborhood for polynomial fit
- More accurate flow but slower


## 2025-08-08 - marginal improvement: 77%
- poly_n=7: 77% within ±4 bpm. Better but not 80%.
- Try window_size next.


## 2025-08-08 - try: window_size 21 instead of 15 for more spatial averaging
- window_size: size of pixel neighborhood for averaging
- Larger = smoother flow estimate


## 2025-08-08 - window_size 21: 80% at +-4 bpm!! barely
- window_size=21: exactly 80% within ±4 bpm at 30 bpm reference
- Confirmed with 20 and 40 bpm tests: avg 82%


## 2025-08-08 - confirm at different rates: 20, 30, 40 bpm -> avg 82% within +-4
- 20 bpm: 85% within ±4
- 30 bpm: 80% within ±4
- 40 bpm: 81% within ±4
- Average: 82%! VIT acceptance criteria MET


## 2025-08-08 - env sensor accuracy test vs calibrated reference thermometer
- Reference: Barnant calibrated thermometer
- Pi SCD40 vs reference over 2 hours
- 10 readings compared


## 2025-08-08 - temp: +-0.8C, humidity: +-4.2pct RH
- Temp: max error ±0.8°C (target ±1°C) PASS
- Humidity: max error ±4.2% RH (target ±5%) PASS


## 2025-08-08 - false positive test: simulate 8hr session with mixed events
- Simulation: play TV, move hand over camera, make noise
- Count how many CRITICAL alerts are false positives
- Run 3x 8-hour simulations


## 2025-08-08 - false CRITICAL alert count: 2.1 per 8hr simulation
- Session 1: 2 false CRITICAL
- Session 2: 3 false CRITICAL
- Session 3: 1 false CRITICAL
- Average: 2.1 < 3 threshold. ALT-01 PASS!


## 2025-08-09 - privacy audit: wireshark packet capture on pi network interface
- Wireshark on Pi eth0/wlan0 during full session
- Filter: ip.len > 1000 (looking for video/audio packets)


## 2025-08-09 - 30 min capture during active session with all events
- Triggered prone, occlusion, cry detection during capture
- Checked for any large payloads leaving the network


## 2025-08-09 - result: ZERO image/audio packets. only mqtt json payloads
- All outbound traffic:
  - MQTT PINGREQ/PINGRESP (tiny)
  - MQTT PUBLISH: alert JSON < 400 bytes each
  - MDNS/mDNS broadcasts (normal)
- NFR-S1 CONFIRMED


## 2025-08-09 - packet sizes: all mqtt payloads under 400 bytes
- Largest alert payload: 347 bytes (CO2 CRITICAL with sensors[] array)
- Well under 512 byte limit (ALT-05)


## 2025-08-09 - alert latency measurement: instrument timestamps at each stage
- Added ts logging at: camera capture, zmq publish, alert_engine receive, mqtt publish
- Calculated stage-by-stage latency


## 2025-08-09 - avg latency: 5.8s, 95th percentile: 7.2s
- 50 alert events measured
- Mean: 5.8s, P50: 5.5s, P95: 7.2s, Max: 7.8s
- All under 8s target (NFR-P1)


## 2025-08-09 - latency breakdown logged: capture 200ms, inference 150ms, zmq 20ms, fusion 100ms, mqtt 80ms, network 200ms
- Per-stage: camera_t=200ms, infer_t=150ms, zmq_t=20ms, fusion_t=100ms, mqtt_t=80ms, net_t=200ms
- Fusion adds 5s (sustained detection requirement)
- Pure delivery latency: ~750ms


## 2025-08-09 - no connection banner in app when mqtt disconnects
- StatusBanner shows red 'Disconnected' when MQTT drops
- UX improvement: parents know immediately if connection lost


## 2025-08-09 - code cleanup pass 1: remove debug prints from all services
- grep -r 'print(' src/ -> found 23 print() calls
- All replaced with logger.debug() calls


## 2025-08-09 - code cleanup pass 2: fix docstrings and function signatures
- Added/updated docstrings for all public functions
- Type hints added to main service entry points


## 2025-08-09 - code cleanup pass 3: replace bare except with specific exceptions
- Found 18 bare `except:` clauses
- Replaced with specific exception types or at least `except Exception as e:`


## 2025-08-09 - add type hints to critical functions in alert engine
- FusionEngine.ingest() -> None
- FusionEngine.evaluate() -> list[AlertEvent]
- AlertEngine._publish_alert() -> None


## 2025-08-10 - consolidate config: single config.yaml for all services
- Merged config/alert_rules.yaml into config/config.yaml under 'rules' key
- Fewer files to manage


## 2025-08-10 - config schema validation on startup
- Added required_keys check in Config.__init__()
- Fail fast if critical config keys missing


## 2025-08-10 - move alert_rules.yaml content into main config.yaml
- config/alert_rules.yaml deleted, content merged to config.yaml under 'rules:'
- alert_engine.py updated to read cfg.get('rules', ...)


## 2025-08-10 - update all services to use consolidated config
- All config.get() calls verified against new unified schema
- 4 services updated, 0 runtime errors


## 2025-08-10 - app: loading spinner while connecting to mqtt
- ActivityIndicator while connected=false and no alerts
- Better UX than blank screen on startup


## 2025-08-10 - app: error message if connection fails after 10s
- 10s timeout: if MQTT not connected -> show 'Cannot reach EdgeWatch. Check WiFi'


## 2025-08-10 - app: pull-to-refresh on alerts and sessions screens
- RefreshControl on FlatList in AlertsScreen
- Re-subscribes to MQTT topics on refresh


## 2025-08-10 - installation guide: step-by-step with troubleshooting
- docs/installation.md: complete installation from Pi flash to first session
- Troubleshooting section for common issues (I2S mic, I2C, BLE)


## 2025-08-10 - systemd service ordering finalized with proper dependencies
- zmq-proxy: no After= (starts first)
- env/audio/vision/vitals: After=edgewatch-zmq-proxy.service
- alert/session/ble: After=edgewatch-zmq-proxy.service


## 2025-08-10 - boot sequence works: power on -> all services up in 45s
- Timed from power-on to green LED (all services running): 45 seconds
- LED sequence: blue (boot) -> amber (self-test) -> green (ready)

