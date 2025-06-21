# EdgeWatch
Edge AI Infant Monitoring System — Non-contact, privacy-first, fully on-device.

## Overview
Ceiling/wall-mounted sensor pod monitors a sleeping infant using camera (pose/occlusion),
microphone (cry + breathing), environmental sensors (CO2, temp, humidity, VOC),
and optionally 60GHz mmWave radar. All ML inference runs on Raspberry Pi 4. No video
or audio leaves the device.

## Status
Under active development — Final Year Engineering Grand Project

## Hardware
- Raspberry Pi 4 (4GB)
- RPi Camera Module v2 + wide-angle IR lens
- INMP441 I2S MEMS Microphone
- Sensirion SCD40 (CO2 + temp + humidity)
- SGP30 (VOC)
- BH1750 (ambient light)
- 940nm IR LED ring

## Author
Ramil — Solo developer, Final Year Grand Project 2025
