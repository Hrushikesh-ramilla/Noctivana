#!/usr/bin/env python3
"""BH1750 ambient light sensor test."""
import smbus2, time

ADDR = 0x23
bus  = smbus2.SMBus(1)
bus.write_byte(ADDR, 0x10)  # continuous high-res mode
time.sleep(0.12)
for _ in range(5):
    d = bus.read_i2c_block_data(ADDR, 0, 2)
    lux = ((d[0]<<8)+d[1]) / 1.2
    print(f"  Lux: {lux:.1f}")
    time.sleep(1)
bus.close()
