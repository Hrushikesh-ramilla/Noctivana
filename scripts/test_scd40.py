#!/usr/bin/env python3
"""SCD40 CO2/Temp/Humidity sensor test. CO2 needs 5min warmup."""
import smbus2, time

SCD40_ADDR = 0x44

def cmd(bus, b, delay=0.005):
    bus.write_i2c_block_data(SCD40_ADDR, b[0], list(b[1:]))
    time.sleep(delay)

def read(bus):
    cmd(bus, [0x21, 0x9D]); time.sleep(5)
    d = bus.read_i2c_block_data(SCD40_ADDR, 0xEC, 9)
    co2  = (d[0]<<8)|d[1]
    temp = -45 + 175 * ((d[3]<<8)|d[4]) / 65535.0
    rh   = 100  * ((d[6]<<8)|d[7]) / 65535.0
    return co2, round(temp,2), round(rh,2)

bus = smbus2.SMBus(1)
cmd(bus,[0x3F,0x86]); time.sleep(0.5)
print("Warming up 30s...")
time.sleep(30)
for _ in range(3):
    co2,t,h = read(bus)
    print(f"  CO2:{co2}ppm  Temp:{t}C  RH:{h}%")
bus.close()
