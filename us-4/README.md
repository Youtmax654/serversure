# MQTT Environmental Monitoring System (US-4)

## Description

This project implements an advanced environmental monitoring system using an Arduino Uno with Ethernet connectivity. It reads temperature, humidity, and ambient light levels, displaying data on a 16x2 RGB LCD screen and publishing sensor readings to an MQTT broker in real-time. This system is designed for IoT applications where remote monitoring and data aggregation are required.

## Features

- **MQTT Integration**: Publishes sensor data to an MQTT broker for remote monitoring
- **Ethernet Connectivity**: Uses DHCP to automatically configure network settings
- **Temperature & Humidity Monitoring**: Reads data from a DHT11 sensor
- **Advanced Light Intensity Detection**: Measures ambient light using LDR with calibrated lux conversion
- **Real-time Display**: Shows temperature, humidity, and light level on a 16x2 RGB LCD
- **Status Indicators**: LCD color changes to indicate connection state (Green = Connected, Orange = Attempting, Red = Error)
- **Non-blocking Operations**: Uses timers instead of delays for responsive operation

## Hardware Requirements

- **Microcontroller**: Arduino Uno
- **Network Module**: Ethernet Shield (with MAC address: 90:A2:DA:10:DD:F9)
- **Temperature & Humidity Sensor**: Grove DHT11 (connected to pin 2)
- **Light Sensor**: LDR (Light Dependent Resistor) on analog pin A0
- **Display**: Grove LCD RGB Backlight (16x2 characters, I2C interface)
- **Network**: Ethernet connectivity with access to MQTT broker at `10.160.24.211`

## Dependencies

This project uses the following libraries (managed via PlatformIO):

- `Grove - LCD RGB Backlight` (v1.0.2+)
- `Grove Temperature And Humidity Sensor` (v2.0.2+)
- `PubSubClient` (v2.8+) - MQTT client library
- `Ethernet` (v2.0.2+) - Arduino Ethernet Shield library

## Installation

1. Ensure PlatformIO is installed in your IDE (VS Code or compatible)
2. Open the project folder in PlatformIO
3. Update network configuration in `main.cpp`:
   - Modify the `mac[]` array if using a different Ethernet Shield
   - Update `server` IP address if your MQTT broker is on a different address
4. The required libraries will be installed automatically
5. Upload the firmware to your Arduino Uno

## Configuration

### Network Settings
- **MAC Address**: `90:A2:DA:10:DD:F9` (modify if needed)
- **MQTT Server**: `10.160.24.211:1883`
- **DHCP**: Enabled (automatic IP configuration)

### Sensor Pinout
- **DHT11**: Pin 2
- **LDR**: Analog pin A0
- **LCD**: I2C bus (SDA/SCL)

### MQTT Topic
- **Publishing Topic**: `salle/sensors`

## Usage

1. Connect all sensors to the Arduino according to the pin configuration
2. Ensure the Arduino is connected to the network via Ethernet
3. Upload the sketch to the Arduino Uno
4. The system will:
   - Display "Connexion reseau" on startup
   - Attempt DHCP configuration and display the assigned IP
   - Connect to the MQTT broker
   - Publish sensor readings every 5 seconds

5. Subscribe to `salle/sensors` on your MQTT client to receive updates

## Data Format

### MQTT Payload
Data is published as JSON format every 5 seconds:
```json
{"temp": 24, "hum": 65, "lux": 3500}
```

### LCD Display
- **Line 1**: `Lum: [value] lux` (Light level)
- **Line 2**: `T: [temp]*C  H: [humidity]%` (Temperature and Humidity)

### Serial Output
```
Publish: {"temp":24, "hum":65, "lux":3500}
```

## Connection Status Indicators

The LCD backlight color indicates the system status:

- **Green**: Successfully connected to MQTT broker
- **Orange**: Attempting to connect to MQTT broker (retrying every 5 seconds)
- **Red**: DHCP configuration failed
- **White**: Initialization and network configuration phase

## Light Intensity Calibration

The system uses a calibrated formula to convert LDR analog readings to lux values:

$$V_2 = \frac{5}{1024} \times \text{RawADC}$$

$$R_1 = \left(\frac{5}{V_2} - 1\right) \times R_2$$

$$\text{Lux} = B \times R_1^m$$

Where:
- $R_2 = 10k\Omega$ (series resistor)
- $B = 1.3 \times 10^7$ (sensor constant)
- $m = -1.4$ (exponent for LDR response curve)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| LCD shows "Erreur DHCP" | Verify Ethernet connection and network availability |
| Orange color persists | Check MQTT broker address and availability |
| No sensor readings | Verify DHT11 and LDR connections on pins 2 and A0 |
| MQTT data not received | Confirm MQTT broker is running and accessible at `10.160.24.211:1883` |
| Inaccurate light readings | Recalibrate the lux conversion formula constants based on your sensor |

## Performance Notes

- Sensor readings are taken every 5 seconds (non-blocking)
- DHT11 readings may be up to 2 seconds old
- Network operations do not block sensor reading cycles
- Maximum JSON payload size: 100 characters
