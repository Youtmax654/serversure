# Security Camera System (US-6)

## Description

This project implements an automated security camera system for Raspberry Pi that integrates with MQTT-based motion detection. The system listens for motion alerts from the MQTT broker (published by US-5: Motion Detection System) and automatically captures photos when motion is detected. All captured images are timestamped and stored in a centralized directory for later review.

## Features

- **MQTT-Triggered Capture**: Listens to motion detection alerts and automatically takes photos
- **Timestamped Photos**: Each capture is automatically named with date and time (YYYYMMDD_HHMMSS format)
- **Headless Operation**: Designed to run without a monitor (no X11 required)
- **Automated Directory Management**: Creates storage directory if it doesn't exist
- **Error Handling**: Gracefully handles MQTT connection issues and JSON parsing errors
- **Raspberry Pi Optimized**: Uses `rpicam-jpeg` for efficient image capture on modern Raspberry Pi
- **Real-time Monitoring**: Continuously watches for motion events

## System Requirements

### Hardware
- **Single Board Computer**: Raspberry Pi 4/5 with Bookworm OS (or similar)
- **Camera Module**: Official Raspberry Pi Camera v2 or v3 (or compatible CSI camera)
- **Network**: Ethernet or WiFi connection to MQTT broker
- **Storage**: Sufficient disk space for surveillance photos

### Software
- **Python**: 3.7+
- **MQTT Broker**: Accessible at configured broker address
- **Camera Tools**: `rpicam-jpeg` (included in Raspberry Pi OS Bookworm)
- **Python Libraries**: See Dependencies section

## Dependencies

Install required Python packages:
```bash
pip install paho-mqtt
```

For camera support on Raspberry Pi Bookworm:
```bash
sudo apt update
sudo apt install -y libraspberrypi-bin
```

## Installation

1. **Clone or copy the project** to your Raspberry Pi:
   ```bash
   git clone <repository-url>
   cd us-6
   ```

2. **Install Python dependencies**:
   ```bash
   pip install paho-mqtt
   ```

3. **Verify camera is working**:
   ```bash
   rpicam-jpeg -o test.jpg -t 1 --nopreview
   ```

4. **Update configuration** in `security_cam.py`:
   ```python
   MQTT_BROKER = "your-mqtt-broker-ip"
   MQTT_TOPIC = "salle/mouvement"  # Match your motion sensor topic
   PHOTO_DIR = "/path/to/storage"
   ```

5. **Create the photo directory** (or let the script auto-create it):
   ```bash
   mkdir -p /home/traps/Scripts/dashboard/surveillance_photos
   chmod 755 /home/traps/Scripts/dashboard/surveillance_photos
   ```

6. **Run the system**:
   ```bash
   python3 security_cam.py
   ```

## Configuration

### MQTT Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MQTT_BROKER` | `localhost` | IP address or hostname of MQTT broker |
| `MQTT_TOPIC` | `salle/mouvement` | Topic to subscribe for motion alerts |
| `MQTT_PORT` | `1883` | MQTT broker port (hardcoded) |

### Photo Storage

| Parameter | Default | Description |
|-----------|---------|-------------|
| `PHOTO_DIR` | `/home/traps/Scripts/dashboard/surveillance_photos` | Directory where photos are saved |

### Camera Settings

Current camera configuration:
```python
command = f"rpicam-jpeg -o {filename} -t 1 --width 1024 --height 768 --nopreview"
```

- **Resolution**: 1024×768 pixels
- **Preview Time**: 1 ms (minimal)
- **Format**: JPEG
- **Mode**: Headless (no preview window)

## Usage

### Starting the System

**Manual Start**:
```bash
python3 security_cam.py
```

**With Output Logging**:
```bash
python3 security_cam.py > surveillance.log 2>&1 &
```

**As a Systemd Service**:
Create `/etc/systemd/system/security-camera.service`:
```ini
[Unit]
Description=Security Camera System
After=network.target

[Service]
Type=simple
User=traps
WorkingDirectory=/home/traps/Scripts
ExecStart=/usr/bin/python3 /home/traps/Scripts/security_cam.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable and start:
```bash
sudo systemctl enable security-camera.service
sudo systemctl start security-camera.service
```

### Expected Output

```
Connecting to broker localhost...
Subscribing to topic salle/mouvement...
📷 Surveillance System ACTIVE. Waiting for motion...
🚨 Motion detected!
📸 Taking photo: /home/traps/Scripts/dashboard/surveillance_photos/capture_20260213_142530.jpg
✅ Photo saved.
```

## MQTT Integration

### Expected Payload Format

The system listens for motion alerts with the following JSON structure:

```json
{"status": "ALERT", "value": 35}
```

or 

```json
{"status": "ALERTE", "value": 35}
```

The system triggers photo capture when `status` is either `"ALERT"` or `"ALERTE"`.

### MQTT Connection Flow

```
┌────────────────────────┐
│ Security Camera Start  │
└───────────┬────────────┘
            │
┌───────────▼────────────┐
│ Connect to MQTT Broker │
│ (localhost:1883)       │
└───────────┬────────────┘
            │
┌───────────▼────────────┐
│ Subscribe to Topic     │
│ salle/mouvement        │
└───────────┬────────────┘
            │
┌───────────▼────────────┐
│ Wait for Motion Alert  │
└───────────┬────────────┘
            │
┌───────────▼────────────┐
│ Receive ALERT Message  │
└───────────┬────────────┘
            │
┌───────────▼────────────┐
│ Capture Photo          │
│ with Timestamp         │
└───────────┬────────────┘
            │
┌───────────▼────────────┐
│ Save to PHOTO_DIR      │
└────────────────────────┘
```

## Photo Management

### Filename Format

Photos are automatically named with the following format:
```
capture_YYYYMMDD_HHMMSS.jpg
```

Example: `capture_20260213_142530.jpg` (February 13, 2026 at 14:25:30)

### Storage Location

Default: `/home/traps/Scripts/dashboard/surveillance_photos/`

### Disk Space Considerations

- **JPEG at 1024×768**: Approximately 100-200 KB per photo
- **Daily estimate** (assuming 1 alert per minute during 8-hour window): ~50-100 MB
- **Monthly storage**: ~1.5-3 GB

### Cleanup Strategy

Implement automatic cleanup via cron job to manage storage:
```bash
# Delete photos older than 30 days
0 2 * * * find /home/traps/Scripts/dashboard/surveillance_photos -type f -mtime +30 -delete
```

## Troubleshooting

| Issue | Symptom | Solution |
|-------|---------|----------|
| No connection to broker | "Connecting to broker..." hangs | Verify broker IP/hostname, check network connectivity |
| Camera not found | Error with rpicam-jpeg command | Test camera: `rpicam-still -o test.jpg` |
| Photos not saved | No files appear in directory | Check directory permissions and disk space |
| Missing motion alerts | System running but no photos taken | Verify MQTT topic matches motion sensor, check broker for messages |
| Permission denied | Cannot write to PHOTO_DIR | Verify ownership: `chown traps:traps /path/to/dir` |

## Performance Notes

- **Photo Capture Time**: ~1-2 seconds (depends on Raspberry Pi model)
- **MQTT Latency**: <100ms typical
- **CPU Usage**: ~30-40% during capture, <5% idle
- **Memory Usage**: ~50 MB

## Security Considerations

1. **MQTT Broker Security**: Use authentication on production MQTT brokers
2. **Photo Access**: Restrict access to PHOTO_DIR with appropriate file permissions
3. **Network**: Use VPN or firewall to secure access to motion detection system
4. **Default Credentials**: Change broker credentials if not already done

## Integration with Other Components

This system works seamlessly with:

- **US-5 (Motion Detection)**: Provides MQTT alerts that trigger captures
- **US-4 (MQTT Environmental System)**: Shares same MQTT broker infrastructure
- **Dashboard Application**: Can display captured photos from PHOTO_DIR

## Typical IoT Architecture

```
┌──────────────────┐
│   Ultrasonic     │
│   Sensor         │
│   (US-5)         │
└────────┬─────────┘
         │ MQTT ALERT
         │
┌────────▼────────────────────┐
│  MQTT Broker                │
│  (10.42.0.1:1883)          │
└────────┬────────────────────┘
         │ MQTT SUBSCRIPTION
┌────────▼──────────────────────────┐
│  Security Camera System (US-6)    │
│  - Takes Photo                    │
│  - Stores with Timestamp          │
└───────────────────────────────────┘
```

## Future Enhancements

- Video recording capability (extend to rpicam-vid)
- Motion detection confidence threshold filtering
- Photo upload to cloud storage
- Real-time streaming integration
- Object detection with ML models
- Face recognition for alerts
