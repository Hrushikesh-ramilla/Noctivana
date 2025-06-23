#!/usr/bin/env python3
"""I2C bus scanner - detect connected sensors."""
import smbus2, sys

KNOWN = {0x44:"SCD40 (CO2/Temp/RH)", 0x58:"SGP30 (VOC)", 0x23:"BH1750 (Light)"}

def scan(bus_num=1):
    bus = smbus2.SMBus(bus_num)
    found = []
    for addr in range(0x03, 0x78):
        try: bus.read_byte(addr); found.append(addr)
        except OSError: pass
    bus.close()
    if not found:
        print("No I2C devices found!"); sys.exit(1)
    for a in found:
        print(f"  0x{a:02X} - {KNOWN.get(a,'Unknown')}")
    missing = [a for a in KNOWN if a not in found]
    if missing:
        print(f"WARNING: Missing {[hex(a) for a in missing]}")

if __name__ == "__main__":
    scan()
