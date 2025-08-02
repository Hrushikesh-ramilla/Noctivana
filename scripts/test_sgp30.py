#!/usr/bin/env python3
"""SGP30 VOC/CO gas sensor test. 15s warmup needed."""
import smbus2, time

ADDR = 0x58
bus  = smbus2.SMBus(1)
bus.write_i2c_block_data(ADDR, 0x20, [0x03])  # init_air_quality
time.sleep(0.01)
print("Warming up 15s...")
time.sleep(15)
for _ in range(5):
    bus.write_i2c_block_data(ADDR, 0x20, [0x08])
    time.sleep(0.012)
    d = bus.read_i2c_block_data(ADDR, 0, 6)
    tvoc = (d[0]<<8)|d[1]
    eco2 = (d[3]<<8)|d[4]
    print(f"  TVOC:{tvoc}ppb  eCO2:{eco2}ppm")
    time.sleep(1)
bus.close()
