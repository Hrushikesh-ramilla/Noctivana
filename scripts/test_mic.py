#!/usr/bin/env python3
"""I2S mic test for INMP441. dtoverlay=i2s-mmap must be in /boot/config.txt"""
import sounddevice as sd, numpy as np, sys

print("Available audio devices:"); print(sd.query_devices()); print()

def test(device=2, duration=3, sr=16000):
    try:
        rec = sd.rec(int(duration*sr), samplerate=sr, channels=1,
                     dtype="int16", device=device)
        sd.wait()
        rms = float(np.sqrt(np.mean(rec.astype(np.float32)**2)))
        db  = 20*np.log10(rms+1e-9)
        print(f"  RMS:{rms:.0f}  dB:{db:.1f}  samples:{len(rec)}")
        print("PASSED" if rms > 1 else "WARN: very low signal")
    except Exception as e:
        print(f"FAILED: {e}")
        print("Check: dtoverlay=i2s-mmap in /boot/config.txt")
        sys.exit(1)

test()
