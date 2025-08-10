# EdgeWatch Installation Guide

## Step 1: Flash Raspberry Pi OS
- Flash RPi OS Lite 64-bit (Bookworm) via Raspberry Pi Imager
- Enable SSH and set WiFi in Imager settings
- Boot Pi, SSH in: `ssh pi@edgewatch.local`

## Step 2: Hardware Assembly
- Connect camera module (CSI ribbon cable, check orientation!)
- Wire I2C sensors (see docs/wiring.md)
- Connect IR LED circuit (GPIO17 with 2N2222 transistor)
- Mount sensor pod at 1-2m above crib

## Step 3: Software Setup
```bash
git clone https://github.com/ramil/edgewatch.git
cd edgewatch
./scripts/setup.sh
```

## Step 4: TLS Certificates
```bash
./scripts/generate_certs.sh
```

## Step 5: Configure
Edit config/config.yaml:
- Set hardware pin assignments
- Set alert thresholds for your nursery

## Step 6: Calibrate Crib ROI
- Start the system in setup mode (blue LED)
- Open EdgeWatch app -> Setup -> Calibrate

## Step 7: Start Services
```bash
sudo systemctl enable edgewatch-*.service
sudo systemctl start edgewatch-zmq-proxy.service
# Other services start automatically via dependencies
```

## Troubleshooting
| Problem | Solution |
|---------|----------|
| No audio device | Check /boot/config.txt: dtoverlay=i2s-mmap |
| Camera not detected | Check CSI ribbon cable orientation |
| I2C sensors missing | Check SDA/SCL wiring, sudo raspi-config -> enable I2C |
| MQTT disconnects | Check mosquitto.conf keepalive_interval |
| BLE not discoverable | sudo systemctl restart bluetooth |
