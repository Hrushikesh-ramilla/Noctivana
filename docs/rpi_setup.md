# Raspberry Pi Setup Notes

## Hardware
- Raspberry Pi 4 Model B, 4GB RAM
- Raspberry Pi OS Lite 64-bit (Debian Bookworm)
- microSD 64GB high endurance

## Initial Setup
```bash
# Flash RPi OS Lite 64-bit with Raspberry Pi Imager (enable SSH + WiFi)
sudo apt update && sudo apt upgrade -y
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_camera 0
```

## I2S Microphone (INMP441)
Add to /boot/config.txt:
```
dtoverlay=i2s-mmap
```
Then: sudo modprobe snd-soc-simple-card

## Software Dependencies
```bash
sudo apt install -y python3-pip git i2c-tools libopencv-dev
sudo apt install -y libasound2-dev portaudio19-dev
sudo apt install -y libssl-dev libsqlite3-dev  # for sqlcipher
pip3 install -r requirements.txt
```
