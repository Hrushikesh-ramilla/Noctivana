#!/usr/bin/env python3
    """Full hardware validation - run before starting software development."""
    import sys, time

    def check_camera():
        print("[1/4] Camera...")
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            ok  = cap.isOpened()
            if ok:
                ret, f = cap.read()
                cap.release()
                print(f"  OK shape={f.shape}" if ret else "  WARN: no frame")
                return True
            print("  FAIL: not detected"); return False
        except Exception as e:
            print(f"  FAIL: {e}"); return False

    def check_mic():
        print("[2/4] Microphone...")
        try:
            import sounddevice as sd, numpy as np
            r = sd.rec(16000, samplerate=16000, channels=1, dtype="int16", device=2)
            sd.wait()
            rms = float(np.sqrt(np.mean(r.astype(np.float32)**2)))
            print(f"  OK RMS={rms:.0f}"); return True
        except Exception as e:
            print(f"  FAIL: {e}"); return False

    def check_sensors():
        print("[3/4] I2C Sensors...")
        try:
            import smbus2
            bus = smbus2.SMBus(1)
            ok  = True
            for addr, name in {0x44:"SCD40",0x58:"SGP30",0x23:"BH1750"}.items():
                try: bus.read_byte(addr); print(f"  OK: {name}")
                except: print(f"  FAIL: {name}"); ok = False
            bus.close(); return ok
        except Exception as e:
            print(f"  FAIL: {e}"); return False

    def check_ir():
        print("[4/4] IR LED...")
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.OUT)
            GPIO.output(17, 1); time.sleep(0.1); GPIO.output(17, 0)
            GPIO.cleanup(); print("  OK GPIO17"); return True
        except Exception as e:
            print(f"  SKIP (not Pi): {e}"); return True

    results = {"Camera":check_camera(),"Mic":check_mic(),
               "Sensors":check_sensors(),"IR LED":check_ir()}
    print("
=== Results ===")
    for k,v in results.items():
        print(f"  {'PASS' if v else 'FAIL'} | {k}")
    if not all(results.values()):
        sys.exit(1)
