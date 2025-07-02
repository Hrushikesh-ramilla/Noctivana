#!/usr/bin/env python3
"""MoveNet pose detection test on camera frames."""
import cv2, time, sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

MODEL = "models/movenet_lightning.tflite"

try:
    import tflite_runtime.interpreter as tflite
    interp = tflite.Interpreter(MODEL)
    interp.allocate_tensors()
    in_d  = interp.get_input_details()[0]
    out_d = interp.get_output_details()[0]
    print(f"Model input shape:  {in_d['shape']}")
    print(f"Model output shape: {out_d['shape']}")
except Exception as e:
    print(f"ERROR loading model: {e}"); sys.exit(1)

cap = cv2.VideoCapture(0)
for _ in range(30):
    ret, frame = cap.read()
    if not ret: continue
    inp = cv2.resize(frame, (192,192))
    inp = inp.astype(np.uint8)[np.newaxis]
    t0  = time.time()
    interp.set_tensor(in_d["index"], inp)
    interp.invoke()
    kpts = interp.get_tensor(out_d["index"])  # [1,1,17,3]
    dt   = (time.time()-t0)*1000
    print(f"Inference: {dt:.1f}ms  kpts_shape={kpts.shape}")
cap.release()
