#!/usr/bin/env python3
"""Camera test script - basic capture and FPS check."""
import cv2, time, sys

def test_camera(device=0, duration=10):
    cap = cv2.VideoCapture(device)
    if not cap.isOpened():
        print("ERROR: Camera not detected! Check ribbon cable.")
        sys.exit(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    count, start = 0, time.time()
    while time.time() - start < duration:
        ret, frame = cap.read()
        if ret:
            count += 1
    cap.release()
    fps = count / duration
    print(f"Result: {count} frames in {duration}s = {fps:.1f} fps  shape={frame.shape}")
    print("PASSED" if count > 0 else "FAILED")

if __name__ == "__main__":
    test_camera()
