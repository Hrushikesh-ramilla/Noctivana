#!/usr/bin/env python3
"""
Process supervisor: watchdog that monitors and restarts crashed services.
NFR-R2: auto-restart within 30 seconds.
"""
import subprocess, time, signal, sys, logging, os

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s")
logger = logging.getLogger("supervisor")

SERVICES = [
    {"name": "zmq_proxy",       "cmd": ["python3", "src/services/zmq_proxy.py"],       "delay": 0},
    {"name": "env_service",     "cmd": ["python3", "src/services/env_service.py"],      "delay": 2},
    {"name": "audio_service",   "cmd": ["python3", "src/services/audio_service.py"],    "delay": 3},
    {"name": "vision_service",  "cmd": ["python3", "src/services/vision_service.py"],   "delay": 3},
    {"name": "vitals_service",  "cmd": ["python3", "src/services/vitals_service.py"],   "delay": 4},
    {"name": "alert_engine",    "cmd": ["python3", "src/services/alert_engine.py"],     "delay": 5},
    {"name": "session_manager", "cmd": ["python3", "src/services/session_manager.py"],  "delay": 6},
    {"name": "ble_service",     "cmd": ["python3", "src/services/ble_service.py"],       "delay": 7},
]

RESTART_DELAY  = 3   # seconds before restart
HEARTBEAT_S    = 10  # check interval


class Supervisor:
    def __init__(self):
        self._procs  = {}
        self._run    = True
        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT,  self._shutdown)

    def _shutdown(self, *_):
        logger.info("Supervisor shutting down all services...")
        self._run = False
        for name, proc in self._procs.items():
            proc.terminate()
            logger.info(f"  Terminated {name}")
        sys.exit(0)

    def _start(self, svc: dict):
        name = svc["name"]
        try:
            proc = subprocess.Popen(
                svc["cmd"], cwd=os.path.dirname(os.path.dirname(__file__))
            )
            self._procs[name] = proc
            logger.info(f"Started {name} (pid={proc.pid})")
        except Exception as e:
            logger.error(f"Failed to start {name}: {e}")

    def run(self):
        logger.info("Supervisor starting all services...")
        for svc in SERVICES:
            time.sleep(svc["delay"])
            self._start(svc)

        while self._run:
            for svc in SERVICES:
                name = svc["name"]
                proc = self._procs.get(name)
                if proc and proc.poll() is not None:
                    logger.warning(f"{name} crashed (exit={proc.returncode}), restarting in {RESTART_DELAY}s...")
                    time.sleep(RESTART_DELAY)
                    self._start(svc)
            time.sleep(HEARTBEAT_S)


if __name__ == "__main__":
    Supervisor().run()
