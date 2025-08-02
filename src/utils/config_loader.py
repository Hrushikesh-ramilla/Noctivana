#!/usr/bin/env python3
"""YAML config loader with thread-safe access and hot-reload."""
import yaml, os, threading, logging
from typing import Any

logger = logging.getLogger(__name__)


class Config:
    def __init__(self, path: str):
        self._path = path
        self._data = {}
        self._lock = threading.RLock()
        self._callbacks = []
        self.reload()

    def reload(self):
        try:
            with open(self._path) as f:
                new = yaml.safe_load(f)
            with self._lock:
                self._data = new
            logger.info(f"Config loaded: {self._path}")
            for cb in self._callbacks:
                try: cb(self._data)
                except Exception as e: logger.error(f"Config cb error: {e}")
        except Exception as e:
            logger.error(f"Config load failed: {e}")

    def get(self, *keys, default=None) -> Any:
        with self._lock:
            val = self._data
            for k in keys:
                if isinstance(val, dict):
                    val = val.get(k, default)
                else:
                    return default
        return val if val is not None else default

    def on_change(self, cb):
        self._callbacks.append(cb)


_cfg = None

def get_config(path="/home/pi/edgewatch/config/config.yaml") -> Config:
    global _cfg
    if _cfg is None:
        _cfg = Config(path)
    return _cfg
