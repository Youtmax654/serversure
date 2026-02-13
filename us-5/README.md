# Motion Detection System with Ultrasonic Sensor (US-5)

## Description

This project implements a motion/proximity detection system using an ESP32 microcontroller and an ultrasonic distance sensor. It continuously monitors the distance to nearby objects and publishes MQTT alerts when motion is detected (i.e., when an object gets closer than a defined threshold). The system uses state-based logic to avoid flooding the MQTT broker with repeated messages.

## Features

- **Ultrasonic Distance Measurement**: Real-time distance monitoring using Grove Ultrasonic Ranger
- **Motion Detection**: Triggers alerts when objects move within a defined threshold
- **WiFi Connectivity**: Connects to WiFi for MQTT communication
- **MQTT Integration**: Publishes status updates to an MQTT broker
- **State-Based Alerts**: Smart alert system that avoids message flooding
- **Serial Monitoring**: Debug output showing distance measurements and alert events
- **Low Power Efficient**: Uses ESP32 for reliable and efficient operation

## Hardware Requirements

- **Microcontroller**: ESP32 Development Board
- **Distance Sensor**: Grove Ultrasonic Ranger (connected to GPIO pin 4)
- **Power Supply**: 5V USB power for the ESP32
- **Network**: WiFi connectivity to access MQTT broker

## Dependencies

This project uses the following libraries (managed via PlatformIO):

- `Grove Ultrasonic Ranger` (v1.0.1+) - Ultrasonic distance sensor library
- `PubSubClient` (v2.8+) - MQTT client library
- `WiFi` - Built-in ESP32 WiFi library

## Installation

1. Ensure PlatformIO is installed in your IDE (VS Code or compatible)
2. Open the project folder in PlatformIO
3. Configure WiFi and MQTT settings in `main.cpp`:
   ```cpp
   const char *ssid = "your-wifi-ssid";
   const char *password = "your-wifi-password";
   const char *mqtt_server = "your-mqtt-broker-ip";
   const int ALERT_VALUE = 50; // Threshold in cm
   ```
4. The required libraries will be installed automatically
5. Upload the firmware to your ESP32

## Configuration

### Network Settings
- **WiFi SSID**: `rpi-serversure` (default)
- **WiFi Password**: `lc9dAcDY4J` (default)
- **MQTT Server**: `10.42.0.1:1883` (default)
- **MQTT Client ID**: `ESP32_Security_Ultrason`

### Sensor Configuration
- **Ultrasonic Sensor Pin**: GPIO 4
- **Alert Threshold**: 50 cm (distance below this triggers alert)
- **Measurement Interval**: 250 ms

### MQTT Topic
- **Publishing Topic**: `salle/mouvement` (room/motion)

## Usage

1. Update the WiFi SSID, password, and MQTT broker address in `main.cpp`
2. Connect the ultrasonic sensor to GPIO pin 4
3. Upload the sketch to the ESP32
4. Open the Serial Monitor at 115200 baud to view distance readings and alerts
5. The system will:
   - Connect to WiFi automatically
   - Establish MQTT connection
   - Continuously measure distance
   - Publish alerts when motion is detected

## Data Format

### MQTT Payload

The system publishes JSON payloads to `salle/mouvement`:

**Alert State** (when object detected within threshold):
```json
{"status": "ALERT", "value": 35}
```

**Normal State** (when object moves away):
```json
{"status": "OK", "value": 75}
```

Where `value` is the measured distance in centimeters.

### Serial Output
```
Distance: 45 cm
>>> TRIGGER: SENDING ALERT <<<
```

```
Distance: 65 cm
>>> RESTORE: SENDING OK <<<
```

## Operation Logic

### State-Based Alert System

The system maintains an internal state (`inAlertState`) to prevent message flooding:

1. **Initialization**: `inAlertState = false` (no alert)
2. **Detection**: When distance < ALERT_VALUE (50 cm):
   - If not already in alert state, publish ALERT message
   - Set `inAlertState = true`
3. **Clear**: When distance >= ALERT_VALUE or = 0 (no object):
   - If in alert state, publish OK message
   - Set `inAlertState = false`

This ensures only one ALERT message is sent per intrusion event rather than continuous messages.

## Connection Flow

```
┌─────────────────────────┐
│   ESP32 Startup         │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│ Connect to WiFi         │
│ (rpi-serversure)        │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│ Connect to MQTT Broker  │
│ (10.42.0.1:1883)       │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│ Read Ultrasonic Sensor  │
│ Every 250ms             │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│ Publish MQTT Status     │
│ on salle/mouvement      │
└─────────────────────────┘
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| WiFi connection fails | Verify SSID and password are correct |
| MQTT connection fails (rc=1) | Check MQTT broker is running at `10.42.0.1:1883` |
| No distance readings | Verify ultrasonic sensor is connected to GPIO pin 4 |
| Constant alerts | Verify ALERT_VALUE threshold is appropriate for your setup |
| Serial shows garbage | Ensure Serial Monitor baud rate is set to 115200 |
| Sensor returns 0 | Out of range or sensor malfunction; typical range is 2-400 cm |

## Performance Specifications

- **Measurement Range**: 2-400 cm
- **Measurement Accuracy**: ±2 cm
- **Measurement Interval**: 250 ms
- **Response Time**: ~500 ms (2 measurements to detect state change)
- **WiFi**: 802.11 b/g/n (2.4 GHz)
- **MQTT Protocol**: Version 3.1.1

## Power Consumption

- **Idle**: ~80 mA
- **Active (WiFi + MQTT)**: ~150-200 mA

## Notes

- The ultrasonic sensor requires a small object for reliable detection (minimum ~5 cm diameter recommended)
- Large flat surfaces provide better reflectivity
- The 250 ms delay ensures sensor stability and reduces measurement noise
- MQTT messages are sent only on state changes to minimize network traffic
