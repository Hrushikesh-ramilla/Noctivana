#!/usr/bin/env python3
"""I2S microphone abstraction for continuous ring-buffer capture."""
import sounddevice as sd, numpy as np, threading, logging

logger = logging.getLogger(__name__)


class Microphone:
    SAMPLE_RATE = 16000
    CHANNELS    = 1
    DTYPE       = "int16"

    def __init__(self, device_index=2, buffer_seconds=2):
        self.device_index = device_index
        self._buf_size    = int(buffer_seconds * self.SAMPLE_RATE)
        self._buf         = np.zeros(self._buf_size, dtype=np.int16)
        self._wpos        = 0
        self._lock        = threading.Lock()
        self._stream      = None

    def _callback(self, indata, frames, time_info, status):
        if status:
            logger.warning(f"Mic status: {status}")
        data = indata[:, 0]
        with self._lock:
            n = len(data)
            end = self._wpos + n
            if end <= self._buf_size:
                self._buf[self._wpos:end] = data
            else:
                first = self._buf_size - self._wpos
                self._buf[self._wpos:] = data[:first]
                self._buf[:end - self._buf_size] = data[first:]
            self._wpos = end % self._buf_size

    def start(self):
        self._stream = sd.InputStream(
            device=self.device_index, samplerate=self.SAMPLE_RATE,
            channels=self.CHANNELS, dtype=self.DTYPE,
            callback=self._callback, blocksize=512,
        )
        self._stream.start()
        logger.info(f"Mic started on device {self.device_index}")

    def read_window(self, duration_s=0.96):
        """Returns float32 [-1,1] window of audio."""
        n = int(duration_s * self.SAMPLE_RATE)
        with self._lock:
            pos = self._wpos
        start = (pos - n) % self._buf_size
        if start < pos:
            window = self._buf[start:pos].copy()
        else:
            window = np.concatenate([self._buf[start:], self._buf[:pos]])
        return window.astype(np.float32) / 32768.0

    def read_rms_db(self):
        w   = self.read_window(0.25)
        rms = np.sqrt(np.mean(w**2))
        return 20 * np.log10(rms + 1e-9)

    def stop(self):
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def __del__(self):
        self.stop()
