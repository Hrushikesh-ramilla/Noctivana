# Wiring Reference

## I2C Bus (GPIO2=SDA, GPIO3=SCL)
SCD40, SGP30, BH1750 all share the same bus.
Addresses: SCD40=0x44, SGP30=0x58, BH1750=0x23

## I2S Microphone INMP441
GPIO18=SCK, GPIO19=WS, GPIO20=SD, L/R pin tied to GND (left ch)

## IR LED Ring
GPIO17 -> 1kR -> 2N2222 Base | Collector -> IR LED (-) | LED (+) -> 5V (with current-limit resistor)

## Status RGB LED (common-cathode)
GPIO27=Red, GPIO22=Green, GPIO10=Blue  (each via 100R to anode)
