#!/usr/bin/env python3
"""Resource monitor: log CPU, RAM, temperature for all EdgeWatch processes."""
import psutil, time, subprocess

SERVICE_NAMES = ["zmq_proxy","env_service","audio_service","vision_service",
                 "vitals_service","alert_engine","session_manager","ble_service"]

def pi_temp():
    try:
        t = open("/sys/class/thermal/thermal_zone0/temp").read().strip()
        return int(t) / 1000.0
    except Exception:
        return 0.0

def find_procs():
    result = {}
    for proc in psutil.process_iter(["pid","name","cmdline","memory_info","cpu_percent"]):
        try:
            cmd = " ".join(proc.info["cmdline"] or [])
            for svc in SERVICE_NAMES:
                if svc in cmd:
                    result[svc] = proc
        except Exception:
            pass
    return result

print(f"{'Service':<20} {'PID':>6} {'CPU%':>6} {'RAM(MB)':>8} {'Temp(C)':>8}")
print("-" * 60)
while True:
    procs = find_procs()
    temp  = pi_temp()
    for svc in SERVICE_NAMES:
        p = procs.get(svc)
        if p:
            try:
                cpu = p.cpu_percent(interval=0.1)
                ram = p.memory_info().rss // (1024*1024)
                print(f"{svc:<20} {p.pid:>6} {cpu:>6.1f} {ram:>8} {temp:>8.1f}")
            except Exception:
                print(f"{svc:<20} {'?':>6} {'?':>6} {'?':>8} {temp:>8.1f}")
        else:
            print(f"{svc:<20} {'N/A':>6}")
    print()
    time.sleep(60)
