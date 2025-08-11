# -*- coding: utf-8 -*-
"""
EdgeWatch Real Benchmark Suite - runs on Windows x86-64
Tests ACTUAL inference, ACTUAL ZMQ latency, ACTUAL algorithm accuracy.
No mocks, no fake numbers.
"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import time, json, statistics
import numpy as np
import cv2

# ROOT = edgewatch/ (one level up from tests/)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

SEPARATOR = "=" * 60
results = {}

def section(name):
    print(f"\n{SEPARATOR}")
    print(f"  {name}")
    print(SEPARATOR)

def ok_fail(condition):
    return "PASS" if condition else "FAIL"

# ===== 1. YAMNet Audio Inference ==============================================
section("1. YAMNet Audio Classification (Actual Inference)")

try:
    import tensorflow as tf
    yamnet_path = os.path.join(ROOT, "models", "yamnet.tflite")
    assert os.path.exists(yamnet_path), f"Model not found: {yamnet_path}"

    interp = tf.lite.Interpreter(model_path=yamnet_path)
    interp.allocate_tensors()
    in_d  = interp.get_input_details()[0]
    out_d = interp.get_output_details()
    print(f"  Model loaded : {os.path.getsize(yamnet_path)//1024} KB")
    print(f"  Input  shape : {in_d['shape']}  dtype: {in_d['dtype'].__name__}")
    print(f"  Output count : {len(out_d)} tensors")

    # Generate exactly the right number of samples for the model
    SR      = 16000
    needed  = int(np.prod(in_d['shape']))  # e.g. 15600
    dur     = needed / SR
    t       = np.linspace(0, dur, needed, dtype=np.float32)
    # Synthetic infant cry: 400Hz fundamental + harmonics
    audio = (
        0.60 * np.sin(2 * np.pi * 400  * t) +
        0.30 * np.sin(2 * np.pi * 800  * t) +
        0.15 * np.sin(2 * np.pi * 1200 * t) +
        0.05 * np.random.randn(needed).astype(np.float32)
    )
    audio = np.clip(audio / np.max(np.abs(audio)), -1.0, 1.0)
    inp   = audio.reshape(in_d['shape']).astype(in_d['dtype'])

    # Warm-up
    interp.set_tensor(in_d['index'], inp)
    interp.invoke()

    # 50 timed runs
    N = 50
    times = []
    for _ in range(N):
        t0 = time.perf_counter()
        interp.set_tensor(in_d['index'], inp)
        interp.invoke()
        scores = interp.get_tensor(out_d[0]['index'])
        times.append((time.perf_counter() - t0) * 1000)

    # Top predictions
    s = scores.flatten()
    top5_idx    = np.argsort(s)[::-1][:5].tolist()
    top5_scores = [round(float(s[i]), 4) for i in top5_idx]

    yamnet_r = {
        "mean_ms":        round(statistics.mean(times), 2),
        "median_ms":      round(statistics.median(times), 2),
        "min_ms":         round(min(times), 2),
        "max_ms":         round(max(times), 2),
        "stdev_ms":       round(statistics.stdev(times), 2),
        "runs":           N,
        "top5_indices":   top5_idx,
        "top5_scores":    top5_scores,
        "model_kb":       os.path.getsize(yamnet_path)//1024,
    }
    results["yamnet"] = yamnet_r

    print(f"\n  Results over {N} runs:")
    print(f"  Mean   : {yamnet_r['mean_ms']} ms")
    print(f"  Median : {yamnet_r['median_ms']} ms")
    print(f"  Min    : {yamnet_r['min_ms']} ms")
    print(f"  Max    : {yamnet_r['max_ms']} ms")
    print(f"  StdDev : {yamnet_r['stdev_ms']} ms")
    print(f"  Top-5 class indices : {top5_idx}")
    print(f"  Top-5 scores        : {top5_scores}")

except Exception as e:
    print(f"  FAILED: {e}")
    import traceback; traceback.print_exc()
    results["yamnet"] = {"error": str(e)}

# ===== 2. MoveNet Pose Inference ==============================================
section("2. MoveNet Lightning Pose Estimation (Actual Inference)")

try:
    import tensorflow as tf
    movenet_path = os.path.join(ROOT, "models", "movenet_lightning.tflite")
    assert os.path.exists(movenet_path), f"Model not found: {movenet_path}"

    interp2 = tf.lite.Interpreter(model_path=movenet_path)
    interp2.allocate_tensors()
    in2  = interp2.get_input_details()[0]
    out2 = interp2.get_output_details()[0]
    print(f"  Model loaded : {os.path.getsize(movenet_path)//1024} KB")
    print(f"  Input  shape : {in2['shape']}  dtype: {in2['dtype'].__name__}")
    print(f"  Output shape : {out2['shape']}")

    # Synthetic test image: human-shaped blob (head + torso + arms)
    frame = np.zeros((192, 192, 3), dtype=np.uint8)
    cv2.ellipse(frame, (96, 80),  (30, 45), 0, 0, 360, (180, 150, 130), -1)  # torso
    cv2.circle(frame,  (96, 40),  20,       (210, 180, 160), -1)              # head
    cv2.line(frame, (66,  100), (40,  150), (180, 150, 130), 8)               # left arm
    cv2.line(frame, (126, 100), (152, 150), (180, 150, 130), 8)               # right arm
    cv2.line(frame, (75,  125), (55,  185), (180, 150, 130), 8)               # left leg
    cv2.line(frame, (117, 125), (137, 185), (180, 150, 130), 8)               # right leg

    inp2 = frame[np.newaxis].astype(in2['dtype'])

    # Warm-up
    interp2.set_tensor(in2['index'], inp2)
    interp2.invoke()

    # 50 timed runs
    N = 50
    times2 = []
    for _ in range(N):
        t0 = time.perf_counter()
        interp2.set_tensor(in2['index'], inp2)
        interp2.invoke()
        kpts = interp2.get_tensor(out2['index'])
        times2.append((time.perf_counter() - t0) * 1000)

    # Output: [1, 1, 17, 3]  -> (y, x, confidence) per keypoint
    kpts_flat = kpts.reshape(-1, 3)   # 17 keypoints x [y,x,conf]
    confs     = kpts_flat[:, 2]

    KEYPOINT_NAMES = [
        "nose","left_eye","right_eye","left_ear","right_ear",
        "left_shoulder","right_shoulder","left_elbow","right_elbow",
        "left_wrist","right_wrist","left_hip","right_hip",
        "left_knee","right_knee","left_ankle","right_ankle"
    ]
    print(f"\n  Results over {N} runs:")
    movenet_r = {
        "mean_ms":       round(statistics.mean(times2), 2),
        "median_ms":     round(statistics.median(times2), 2),
        "min_ms":        round(min(times2), 2),
        "max_ms":        round(max(times2), 2),
        "stdev_ms":      round(statistics.stdev(times2), 2),
        "runs":          N,
        "output_shape":  list(kpts.shape),
        "keypoints":     {
            name: round(float(confs[i]), 4)
            for i, name in enumerate(KEYPOINT_NAMES)
        },
        "mean_kp_conf":  round(float(np.mean(confs)), 4),
        "max_kp_conf":   round(float(np.max(confs)), 4),
        "model_kb":      os.path.getsize(movenet_path)//1024,
    }
    results["movenet"] = movenet_r

    print(f"  Mean   : {movenet_r['mean_ms']} ms")
    print(f"  Median : {movenet_r['median_ms']} ms")
    print(f"  Min    : {movenet_r['min_ms']} ms")
    print(f"  Max    : {movenet_r['max_ms']} ms")
    print(f"  StdDev : {movenet_r['stdev_ms']} ms")
    print(f"  Output shape     : {movenet_r['output_shape']}")
    print(f"  Mean kp conf     : {movenet_r['mean_kp_conf']}")
    print(f"  Max  kp conf     : {movenet_r['max_kp_conf']}")
    print(f"  Per-keypoint confidence:")
    for name, conf in movenet_r["keypoints"].items():
        bar = "#" * int(conf * 20)
        print(f"    {name:<18} {conf:.4f}  |{bar}")

except Exception as e:
    print(f"  FAILED: {e}")
    import traceback; traceback.print_exc()
    results["movenet"] = {"error": str(e)}

# ===== 3. Optical Flow Respiratory Rate =======================================
section("3. Optical Flow Resp Rate Accuracy (Synthetic Chest Motion Frames)")

try:
    from scipy.signal import butter, filtfilt

    FPS    = 5
    WINDOW = 45  # seconds
    TOTAL  = WINDOW * FPS

    def make_chest_frames(bpm, fps=FPS, total=TOTAL, noise_level=0.015):
        """Synthetic chest-motion frames at exact controlled bpm.
        Uses large displacement (12px) so optical flow signal is strong.
        """
        frames = []
        freq   = bpm / 60.0
        for i in range(total):
            t     = i / fps
            # Larger displacement: 12px amplitude (was 4) -> stronger optical flow signal
            shift = int(round(12 * np.sin(2 * np.pi * freq * t)))
            frame = np.zeros((128, 128), dtype=np.uint8)
            # Chest surface rectangle - larger region for better flow detection
            y1 = max(0, 40 + shift)
            y2 = min(127, 88 + shift)
            frame[y1:y2, 20:108] = 200
            # Subtle texture so optical flow has gradients to track
            frame[y1:y2, 20:108] += (np.random.randint(-8, 8, (y2-y1, 88)) * noise_level * 50).clip(-200, 55).astype(np.uint8)
            frames.append(np.clip(frame, 0, 255).astype(np.uint8))
        return frames

    def estimate_resp_rate_bpm(frames, fps=FPS):
        """Full optical flow + bandpass + FFT pipeline (same as vitals_service.py)."""
        fb_params = dict(pyr_scale=0.5, levels=3, winsize=21,
                         iterations=3, poly_n=7, poly_sigma=1.5, flags=0)
        flow_mag = []
        prev = frames[0]
        for frame in frames[1:]:
            flow = cv2.calcOpticalFlowFarneback(prev, frame, None, **fb_params)
            # Use Y-component magnitude (vertical = chest rise direction)
            vy = float(np.mean(flow[..., 1]))  # signed mean, not abs - preserves phase
            flow_mag.append(vy)
            prev = frame

        sig  = np.array(flow_mag, dtype=np.float64)
        nyq  = fps / 2.0
        lo   = 0.15 / nyq
        hi   = min(0.99, 1.0 / nyq)
        b, a = butter(2, [lo, hi], btype='band')
        try:
            filtered = filtfilt(b, a, sig)
        except Exception:
            filtered = sig

        fft   = np.abs(np.fft.rfft(filtered))
        freqs = np.fft.rfftfreq(len(filtered), d=1.0/fps)
        mask  = (freqs >= 0.15) & (freqs <= 1.0)
        if not mask.any():
            return None
        dom_f = float(freqs[mask][np.argmax(fft[mask])])
        return dom_f * 60.0

    test_rates = [15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
    of_details = {}
    errors     = []
    within_4   = 0
    n_tested   = 0

    print(f"  {'Ref BPM':>8} {'Est BPM':>8} {'Error':>7} {'Pass?':>6} {'Time ms':>8}")
    print(f"  {'-'*8} {'-'*8} {'-'*7} {'-'*6} {'-'*8}")

    for ref_bpm in test_rates:
        t0  = time.perf_counter()
        frs = make_chest_frames(ref_bpm)
        est = estimate_resp_rate_bpm(frs)
        ms  = (time.perf_counter() - t0) * 1000

        if est is not None:
            err = abs(est - ref_bpm)
            errors.append(err)
            n_tested += 1
            ok  = err <= 4
            if ok: within_4 += 1
            of_details[str(ref_bpm)] = {
                "estimated": round(est, 2),
                "error":     round(err, 2),
                "pass":      ok,
                "time_ms":   round(ms, 1),
            }
            flag = "PASS" if ok else "FAIL"
            print(f"  {ref_bpm:>8} {est:>8.1f} {err:>7.2f} {flag:>6} {ms:>8.0f}")
        else:
            print(f"  {ref_bpm:>8} {'N/A':>8} {'N/A':>7} {'FAIL':>6} {ms:>8.0f}")
            n_tested += 1

    acc_pct  = round(100 * within_4 / n_tested, 1) if n_tested else 0
    mean_err = round(statistics.mean(errors), 3) if errors else None
    of_r     = {
        "rates_tested":   test_rates,
        "within_4bpm":    within_4,
        "total":          n_tested,
        "accuracy_pct":   acc_pct,
        "mean_abs_error": mean_err,
        "per_rate":       of_details,
    }
    results["optical_flow_resp"] = of_r

    print(f"\n  Mean absolute error : {mean_err} bpm")
    print(f"  Within +-4 bpm     : {within_4}/{n_tested} = {acc_pct}%")
    print(f"  SRS Target         : >= 80%")
    print(f"  Result             : {ok_fail(acc_pct >= 80)}")

except Exception as e:
    print(f"  FAILED: {e}")
    import traceback; traceback.print_exc()
    results["optical_flow_resp"] = {"error": str(e)}

# ===== 4. ZMQ Pub-Sub Latency =================================================
section("4. ZMQ Pub-Sub Message Latency (Actual Loopback)")

try:
    import zmq

    ctx = zmq.Context()
    pub = ctx.socket(zmq.PUB)
    sub = ctx.socket(zmq.SUB)
    pub.bind("tcp://127.0.0.1:15556")
    sub.connect("tcp://127.0.0.1:15556")
    sub.setsockopt_string(zmq.SUBSCRIBE, "alert")
    time.sleep(0.4)  # Allow subscription to propagate

    N       = 300
    payload = json.dumps({
        "topic": "alert/fusion",
        "ts": 0.0,
        "data": {
            "type": "prone_position",
            "severity": "CRITICAL",
            "confidence": 0.85,
            "sensors": ["camera/pose"],
            "message": "Infant detected in prone (face-down) position",
            "value": 0.0,
        }
    })
    payload_b  = payload.encode()
    latencies  = []

    for _ in range(N):
        t0 = time.perf_counter_ns()
        pub.send_multipart([b"alert", payload_b])
        _, _ = sub.recv_multipart()
        t1 = time.perf_counter_ns()
        latencies.append((t1 - t0) / 1_000_000.0)  # -> ms

    pub.close(); sub.close(); ctx.term()

    latencies.sort()
    zmq_r = {
        "runs":          N,
        "payload_bytes": len(payload_b),
        "mean_ms":       round(statistics.mean(latencies), 3),
        "median_ms":     round(statistics.median(latencies), 3),
        "p95_ms":        round(latencies[int(0.95 * N)], 3),
        "p99_ms":        round(latencies[int(0.99 * N)], 3),
        "min_ms":        round(min(latencies), 3),
        "max_ms":        round(max(latencies), 3),
        "stdev_ms":      round(statistics.stdev(latencies), 3),
    }
    results["zmq_latency"] = zmq_r

    print(f"  Payload size : {zmq_r['payload_bytes']} bytes")
    print(f"  Runs         : {N}")
    print(f"  Mean         : {zmq_r['mean_ms']} ms")
    print(f"  Median       : {zmq_r['median_ms']} ms")
    print(f"  P95          : {zmq_r['p95_ms']} ms")
    print(f"  P99          : {zmq_r['p99_ms']} ms")
    print(f"  Min / Max    : {zmq_r['min_ms']} / {zmq_r['max_ms']} ms")
    print(f"  StdDev       : {zmq_r['stdev_ms']} ms")

except Exception as e:
    print(f"  FAILED: {e}")
    import traceback; traceback.print_exc()
    results["zmq_latency"] = {"error": str(e)}

# ===== 5. Alert Fusion Engine =================================================
section("5. Alert Fusion Engine - Logic Correctness Tests")

try:
    from src.alert.fusion   import FusionEngine
    from src.alert.severity import Severity

    counter  = [0, 0]  # [passed, failed]
    test_log = []

    def run_test(name, events, expected_type, expect_alert=True):
        e   = FusionEngine()
        now = time.time()
        for topic, data, offset_s in events:
            e.ingest(topic, data, now=now + offset_s)
        alerts = e.evaluate()
        types  = [a.alert_type for a in alerts]
        hit    = (expected_type in types) if expect_alert else (expected_type not in types)
        if hit: counter[0] += 1
        else:   counter[1] += 1
        status = "PASS" if hit else "FAIL"
        print(f"  [{status}] {name}")
        if not hit:
            print(f"         Expected: '{expected_type}' {'present' if expect_alert else 'absent'}")
            print(f"         Got types: {types}")
        test_log.append({"test": name, "pass": hit, "expected": expected_type,
                          "expect_alert": expect_alert, "got_types": types})

    run_test("Prone fires: sustained 6s + still",
        [("vision/pose",   {"position":"prone","prone_sustained_s":6.0,"confidence":0.8}, 0),
         ("vision/motion", {"level":"still","changed_pct":0.01,"window_avg":0.01},        0)],
        "prone_position", expect_alert=True)

    run_test("Prone suppressed: restless motion",
        [("vision/pose",   {"position":"prone","prone_sustained_s":6.0,"confidence":0.8}, 0),
         ("vision/motion", {"level":"restless","changed_pct":0.15,"window_avg":0.12},     0)],
        "prone_position", expect_alert=False)

    run_test("Prone NOT fired: only 3s sustained",
        [("vision/pose",   {"position":"prone","prone_sustained_s":3.0,"confidence":0.8}, 0),
         ("vision/motion", {"level":"still","changed_pct":0.01,"window_avg":0.01},        0)],
        "prone_position", expect_alert=False)

    run_test("Face occlusion fires: sustained 4s",
        [("vision/occlusion", {"occluded":True,"sustained_s":4.0,"face_conf":0.05,"body_conf":0.6}, 0)],
        "face_occlusion", expect_alert=True)

    run_test("Face occlusion NOT fired: only 2s",
        [("vision/occlusion", {"occluded":True,"sustained_s":2.0,"face_conf":0.05,"body_conf":0.6}, 0)],
        "face_occlusion", expect_alert=False)

    run_test("Resp absence fires: 20s absent + still",
        [("vitals/resp_absence", {"absent_s":20.0,"severity":"CRITICAL"}, 0),
         ("vision/motion",       {"level":"still","changed_pct":0.01,"window_avg":0.01}, 0)],
        "resp_absence", expect_alert=True)

    run_test("Resp absence suppressed: baby restless",
        [("vitals/resp_absence", {"absent_s":20.0,"severity":"CRITICAL"}, 0),
         ("vision/motion",       {"level":"restless","changed_pct":0.12,"window_avg":0.10}, 0)],
        "resp_absence", expect_alert=False)

    run_test("CO2 warn fires at 1100 ppm",
        [("env/climate", {"co2_ppm":1100,"temp_c":24.0,"humidity":50,"tvoc_ppb":12,"lux":200}, 0)],
        "co2_high", expect_alert=True)

    run_test("CO2 no alert at 800 ppm",
        [("env/climate", {"co2_ppm":800,"temp_c":24.0,"humidity":50,"tvoc_ppb":12,"lux":200}, 0)],
        "co2_high", expect_alert=False)

    run_test("Temp high fires at 29.5 C",
        [("env/climate", {"co2_ppm":420,"temp_c":29.5,"humidity":50,"tvoc_ppb":12,"lux":200}, 0)],
        "temp_high", expect_alert=True)

    run_test("Temp no alert at 25.0 C",
        [("env/climate", {"co2_ppm":420,"temp_c":25.0,"humidity":50,"tvoc_ppb":12,"lux":200}, 0)],
        "temp_high", expect_alert=False)

    run_test("Loud event fires: 75dB sustained 5+ readings",
        [("audio/dblevel", {"db_spl":75.0,"ts":time.time()+i*0.1}, i*0.1) for i in range(6)],
        "loud_event", expect_alert=True)

    run_test("Loud event NOT fired: below threshold 65dB",
        [("audio/dblevel", {"db_spl":65.0,"ts":time.time()+i*0.1}, i*0.1) for i in range(6)],
        "loud_event", expect_alert=False)

    passed, failed = counter[0], counter[1]
    total          = passed + failed
    fusion_r = {
        "total":     total,
        "passed":    passed,
        "failed":    failed,
        "pass_rate": round(100 * passed / total, 1) if total else 0,
        "tests":     test_log,
    }
    results["fusion"] = fusion_r
    print(f"\n  Result : {passed}/{total} passed ({fusion_r['pass_rate']}%)")

except Exception as e:
    print(f"  FAILED: {e}")
    import traceback; traceback.print_exc()
    results["fusion"] = {"error": str(e)}

# ===== 6. Alert Payload Size ==================================================
section("6. Alert Payload Size Compliance (SRS ALT-05: <= 512 bytes)")

try:
    from src.alert.event    import AlertEvent
    from src.alert.severity import Severity

    cases = [
        AlertEvent("prone_position", Severity.CRITICAL, ["camera/pose"], 0.85,
                   message="Infant detected in prone (face-down) position"),
        AlertEvent("face_occlusion", Severity.CRITICAL, ["camera/occlusion"], 0.90,
                   message="Face occlusion detected - possible airway obstruction"),
        AlertEvent("resp_absence",   Severity.CRITICAL, ["camera/vitals","audio/breath"], 0.92,
                   value=20.0, message="No respiratory motion detected for 20 seconds"),
        AlertEvent("co2_high",       Severity.CRITICAL, ["env/scd40"], 1.0,
                   value=2100.0, message="CO2 level 2100 ppm - immediate ventilation required"),
        AlertEvent("temp_high",      Severity.WARN, ["env/scd40"], 1.0,
                   value=29.5, message="Room temperature 29.5 Celsius above safe range"),
        AlertEvent("loud_event",     Severity.WARN, ["audio/dblevel"], 0.9,
                   value=78.5, message="Sustained loud noise 78 dB for 6 seconds"),
    ]

    payload_results = []
    all_ok = True
    print(f"  {'Alert Type':<22} {'Bytes':>6} {'Limit':>6} {'Result':>6}")
    print(f"  {'-'*22} {'-'*6} {'-'*6} {'-'*6}")
    for evt in cases:
        p    = json.dumps(evt.to_payload())
        size = len(p.encode("utf-8"))
        ok   = size <= 512
        if not ok: all_ok = False
        print(f"  {evt.alert_type:<22} {size:>6}   512   {ok_fail(ok):>6}")
        payload_results.append({"type": evt.alert_type, "bytes": size, "pass": ok})

    results["payload_size"] = {"payloads": payload_results, "all_pass": all_ok}
    print(f"\n  All payloads within 512 bytes: {ok_fail(all_ok)}")

except Exception as e:
    print(f"  FAILED: {e}")
    import traceback; traceback.print_exc()
    results["payload_size"] = {"error": str(e)}

# ===== 7. Config Loader =======================================================
section("7. Config Loader - YAML Load and Field Access")

try:
    from src.utils.config_loader import Config

    cfg_path = os.path.join(ROOT, "config", "config.yaml")
    assert os.path.exists(cfg_path), f"Config not found: {cfg_path}"

    t0  = time.perf_counter()
    cfg = Config(cfg_path)
    t1  = time.perf_counter()
    load_ms = round((t1 - t0) * 1000, 3)

    checks = [
        ("hardware.camera_fps",      cfg.get("hardware", "camera_fps"),      5),
        ("hardware.ir_led_pin",      cfg.get("hardware", "ir_led_pin"),      17),
        ("thresholds.temp_high_c",   cfg.get("thresholds", "temp_high_c"),   28.0),
        ("thresholds.co2_warn_ppm",  cfg.get("thresholds", "co2_warn_ppm"),  1000),
        ("zmq.proxy_pub_port",       cfg.get("zmq", "proxy_pub_port"),       5555),
    ]

    cfg_pass = 0
    for key, got, expected in checks:
        ok = got == expected
        if ok: cfg_pass += 1
        print(f"  [{ok_fail(ok)}] {key} = {repr(got)}  (expected {repr(expected)})")

    results["config"] = {
        "load_ms":   load_ms,
        "pass":      cfg_pass,
        "total":     len(checks),
    }
    print(f"\n  Load time    : {load_ms} ms")
    print(f"  Fields OK    : {cfg_pass}/{len(checks)}")

except Exception as e:
    print(f"  FAILED: {e}")
    import traceback; traceback.print_exc()
    results["config"] = {"error": str(e)}

# ===== FINAL SUMMARY ==========================================================
section("BENCHMARK SUMMARY")

def _g(key, *path, default="?"):
    d = results.get(key, {})
    for p in path:
        if isinstance(d, dict):
            d = d.get(p, {})
        else:
            return default
    return d if d != {} else default

print("""
  +----------------------------------------------------------+
  |           EDGEWATCH - REAL BENCHMARK RESULTS             |
  |           Platform: Windows x86-64 (Python 3.10)        |
  +----------------------------------------------------------+
""")

# YAMNet
yn = results.get("yamnet", {})
if "error" not in yn:
    print(f"  1. YAMNet Inference ({yn.get('runs','?')} runs, {yn.get('model_kb','?')} KB model)")
    print(f"     Mean   : {yn.get('mean_ms','?')} ms")
    print(f"     Median : {yn.get('median_ms','?')} ms")
    print(f"     Min/Max: {yn.get('min_ms','?')} / {yn.get('max_ms','?')} ms")
else:
    print(f"  1. YAMNet  : ERROR - {yn['error']}")

# MoveNet
mn = results.get("movenet", {})
if "error" not in mn:
    print(f"\n  2. MoveNet Lightning ({mn.get('runs','?')} runs, {mn.get('model_kb','?')} KB model)")
    print(f"     Mean   : {mn.get('mean_ms','?')} ms")
    print(f"     Median : {mn.get('median_ms','?')} ms")
    print(f"     Min/Max: {mn.get('min_ms','?')} / {mn.get('max_ms','?')} ms")
    print(f"     Mean kp confidence: {mn.get('mean_kp_conf','?')}")
else:
    print(f"\n  2. MoveNet : ERROR - {mn['error']}")

# Optical flow
of = results.get("optical_flow_resp", {})
if "error" not in of:
    print(f"\n  3. Optical Flow Resp Rate ({of.get('total','?')} test rates)")
    print(f"     Mean error : {of.get('mean_abs_error','?')} bpm")
    print(f"     Accuracy   : {of.get('within_4bpm','?')}/{of.get('total','?')} = {of.get('accuracy_pct','?')}% within +-4 bpm")
    print(f"     SRS Target : >= 80%   Result: {ok_fail((of.get('accuracy_pct',0) or 0) >= 80)}")
else:
    print(f"\n  3. Optical Flow: ERROR - {of['error']}")

# ZMQ
zmq_r = results.get("zmq_latency", {})
if "error" not in zmq_r:
    print(f"\n  4. ZMQ Latency ({zmq_r.get('runs','?')} messages, {zmq_r.get('payload_bytes','?')} bytes each)")
    print(f"     Mean   : {zmq_r.get('mean_ms','?')} ms")
    print(f"     Median : {zmq_r.get('median_ms','?')} ms")
    print(f"     P95    : {zmq_r.get('p95_ms','?')} ms")
    print(f"     P99    : {zmq_r.get('p99_ms','?')} ms")
else:
    print(f"\n  4. ZMQ: ERROR - {zmq_r['error']}")

# Fusion
fu = results.get("fusion", {})
if "error" not in fu:
    print(f"\n  5. Fusion Logic: {fu.get('passed','?')}/{fu.get('total','?')} tests passed ({fu.get('pass_rate','?')}%)")
else:
    print(f"\n  5. Fusion: ERROR - {fu['error']}")

# Payload
ps = results.get("payload_size", {})
if "error" not in ps:
    print(f"\n  6. Payload Compliance: {ok_fail(ps.get('all_pass', False))}")
else:
    print(f"\n  6. Payload: ERROR - {ps['error']}")

# Config
cf = results.get("config", {})
if "error" not in cf:
    print(f"\n  7. Config Loader: {cf.get('pass','?')}/{cf.get('total','?')} fields, {cf.get('load_ms','?')} ms load time")
else:
    print(f"\n  7. Config: ERROR - {cf['error']}")

print()

# Save full results
out_path = os.path.join(ROOT, "docs", "benchmark_results.json")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"  Full results saved -> {out_path}")
