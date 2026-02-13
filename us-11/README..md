# Multi-Function Monitoring Station (US-11)

## Description

This project implements a comprehensive multi-function monitoring station using an Arduino Uno with Ethernet connectivity. It serves as both a data collection hub and an alert responder, combining environmental monitoring capabilities with motion detection alerts. The system publishes sensor readings (temperature, humidity, and light level) to an MQTT broker and subscribes to motion alerts, triggering local audio-visual warnings when intrusion is detected.

## Features

- **Dual MQTT Role**: Publishes environmental data AND subscribes to motion alerts
- **Complete Environmental Monitoring**: Temperature, humidity, and advanced light intensity measurement
- **Alert Response System**: LED and buzzer activation on motion detection
- **Visual Feedback**: RGB LCD display with color-coded status indication
- **Ethernet Connectivity**: DHCP-configured network access
- **Multi-Sensory Alerts**: Visual (LED + Red LCD) and auditory (buzzer) warning signals
- **Real-time Display**: Comprehensive sensor data on 16x2 LCD screen
- **Non-blocking Operations**: Timer-based sensor readings every 5 seconds

## Hardware Requirements

- **Microcontroller**: Arduino Uno
- **Network Module**: Ethernet Shield (MAC: 90:A2:DA:10:DD:F9)
- **Sensors**:
  - Grove DHT11 (temperature/humidity) on pin 2
  - LDR (Light Dependent Resistor) on analog pin A0
- **Actuators**:
  - LED with resistor on pin 6
  - Buzzer (piezo speaker) on pin 3
- **Display**: Grove LCD RGB Backlight (16x2 characters)
- **Network**: Ethernet connectivity to MQTT broker at `10.160.24.211`

## Dependencies

Required libraries (managed via PlatformIO):

- `PubSubClient` (v2.8+) - MQTT client
- `Ethernet` (v2.0.2+) - Ethernet Shield
- `Grove Temperature And Humidity Sensor` (v2.0.2+)
- `Grove - LCD RGB Backlight` (v1.0.2+)

## Installation

1. Ensure PlatformIO is installed in your IDE
2. Open the project folder in PlatformIO
3. Update network configuration in `main.cpp`:
   ```cpp
   byte mac[] = {0x90, 0xA2, 0xDA, 0x10, 0xDD, 0xF9};
   IPAddress server(10, 160, 24, 211);
   ```
4. Dependencies will be installed automatically
5. Upload the firmware to Arduino Uno

## Configuration

### Network Settings
- **MAC Address**: `90:A2:DA:10:DD:F9`
- **MQTT Server**: `10.160.24.211:1883`
- **DHCP**: Enabled (automatic IP configuration)

### Sensor & Actuator Pinout
- **DHT11 (Temp/Humidity)**: Pin 2
- **LDR (Light)**: Analog pin A0
- **LED**: Pin 6
- **Buzzer**: Pin 3
- **LCD**: I2C bus (SDA/SCL)

### MQTT Topics
- **Publishing**: `salle/sensors` (environmental data)
- **Subscribing**: `salle/mouvement` (motion alerts)

### Alert Parameters
- **LED Flash Pattern**: 3 pulses (300ms ON, 200ms OFF)
- **Buzzer Frequency**: 1000 Hz
- **Buzzer Duration**: 3 sounds (300ms each)
- **LCD Alert Color**: Red (255, 0, 0)

## Usage

1. Connect all sensors, actuators, and network components
2. Upload the sketch to Arduino Uno
3. Power on the device
4. LCD will display:
   - "Init Reseau..." during startup
   - Once connected: Light level, temperature, and humidity
5. System will:
   - Publish sensor data every 5 seconds to `salle/sensors`
   - Listen continuously for motion alerts on `salle/mouvement`
   - Trigger alerts immediately upon motion detection

## Data Format

### Published Data (to `salle/sensors`)

Publishes every 5 seconds:
```json
{"temp": 23.5, "hum": 55.0, "lux": 3200}
```

### Subscribed Data (from `salle/mouvement`)

Expects format from US-5 motion sensor:
```json
{"status": "ALERT", "value": 35}
```

The system triggers alerts when `"status": "ALERT"` is detected in the message.

## LCD Display Format

**Line 1**: Light level
```
Lum: 3200 lux
```

**Line 2**: Temperature and humidity
```
T:23.5C H:55%
```

## Alert Response System

### Trigger Condition
When the system receives an MQTT message containing `"status": "ALERT"`:

### Response Sequence (3 pulses)

```
PULSE 1:                PULSE 2:                PULSE 3:
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│  LED ON     │        │  LED ON     │        │  LED ON     │
│  BUZZER 1kHz│        │  BUZZER 1kHz│        │  BUZZER 1kHz│
└─────────────┘        └─────────────┘        └─────────────┘
  300ms                  300ms                  300ms
     │                      │                      │
     └─200ms─┘              └─200ms─┘              └─ END

LCD: RED (255,0,0)      LCD: RED (255,0,0)      LCD: WHITE (normal)
```

### Detailed Timing
```
T=0ms   : LED HIGH, BUZZER ON (1000 Hz), LCD RED
T=300ms : LED LOW, BUZZER OFF
T=500ms : LED HIGH, BUZZER ON
T=800ms : LED LOW, BUZZER OFF
T=1000ms: LED HIGH, BUZZER ON
T=1300ms: LED LOW, BUZZER OFF, LCD returns to WHITE
```

## LED Pulse Specifications

- **GPIO Pin**: Pin 6 (PWM capable)
- **Voltage**: 5V
- **Current**: 20 mA typical (with resistor)
- **Pulse Duration**: 300 ms ON, 200 ms OFF
- **Number of Pulses**: 3
- **Total Alert Duration**: ~1.3 seconds

## Buzzer Specifications

- **GPIO Pin**: Pin 3 (PWM capable)
- **Frequency**: 1000 Hz (audible alarm tone)
- **Voltage**: 5V
- **Pulse Duration**: 300 ms ON, 200 ms OFF
- **Number of Pulses**: 3
- **Total Alert Duration**: ~1.3 seconds

## Light Intensity Calibration

The system uses the same calibrated formula as US-4:

$$V_2 = \frac{5}{1024} \times \text{RawADC}$$

$$R_1 = \left(\frac{5}{V_2} - 1\right) \times R_2$$

$$\text{Lux} = B \times R_1^m$$

Where:
- $R_2 = 10k\Omega$
- $B = 1.3 \times 10^7$
- $m = -1.4$

## Connection Status Indicators

LCD backlight color indicates system state:

| Color | State | Meaning |
|-------|-------|---------|
| White (255,255,255) | Normal | System operational, no alerts |
| Green (0,255,0) | Connected | Successfully connected to MQTT |
| Red (255,0,0) | Alert | Motion detected, alert active |

## System Architecture

```
┌─────────────────────────────────┐
│  Arduino Uno Monitoring Station  │
│         (US-11)                 │
├─────────────────────────────────┤
│                                 │
│  ┌─ DHT11 ──────────┐          │
│  │ Temperature      │          │
│  │ Humidity         │          │
│  └──────────────────┘          │
│                                 │
│  ┌─ LDR ────────────┐          │
│  │ Light Level      │          │
│  └──────────────────┘          │
│                                 │
│  ┌─ LED on Pin 6 ──┐          │
│  │ Alert Indicator │          │
│  └──────────────────┘          │
│                                 │
│  ┌─ Buzzer on Pin 3 ─┐        │
│  │ Audio Alert      │          │
│  └──────────────────┘          │
│                                 │
│  ┌─ RGB LCD ────────┐          │
│  │ Display System   │          │
│  └──────────────────┘          │
│                                 │
│  ┌─ Ethernet Shield ───────┐  │
│  │ Network Connectivity    │  │
│  └──────────────────────────┘  │
└──────────┬──────────────────────┘
           │ MQTT
     ┌─────▼─────┐
     │MQTT Broker│
     │ 10.160... │
     └─────┬─────┘
           │
    ┌──────┴──────────┐
    │                 │
┌───▼──┐  (Subscribe) ┌──▼───┐
│US-5  │  salle/      │US-11 │
│Motion◄──mouvement   │Multi │
│      │              │      │
└──────┘              └──┬───┘
                         │ (Publish)
                   salle/sensors
                         │
                    ┌────▼────┐
                    │Dashboard│
                    │  US-8   │
                    │Database │
                    └─────────┘
```

## Integration with Other Components

### Data Publishing (US-11 → Dashboard)
- **Topic**: `salle/sensors`
- **Frequency**: Every 5 seconds
- **Data**: Temperature, humidity, luminosity
- **Consumer**: Dashboard API (US-8 Data Logger)

### Alert Subscription (US-5 → US-11)
- **Topic**: `salle/mouvement`
- **Trigger**: Motion detection alert
- **Action**: LED + Buzzer + LCD alert
- **Source**: Ultrasonic motion sensor (US-5)

## Troubleshooting

| Issue | Symptom | Solution |
|-------|---------|----------|
| LCD shows "Init Reseau..." indefinitely | No network connection | Verify Ethernet cable, check DHCP server |
| No sensor readings on LCD | Blank display after boot | Verify DHT11 and LDR connections on pins 2 and A0 |
| MQTT data not publishing | No data in broker | Check MQTT server address (10.160.24.211:1883) |
| Alerts not triggering | No LED/buzzer response to motion | Verify subscription to `salle/mouvement`, check LED/buzzer pins |
| LED/Buzzer not responding | Alert received but no output | Test pins 3 and 6 with simple blink sketch, verify components |
| Inaccurate light readings | Light values seem wrong | Recalibrate LDR formula constants |
| LCD color stuck on red | Always showing red background | Check callback logic, may indicate continuous alert |

## Performance Characteristics

- **Sensor Reading Interval**: 5 seconds (non-blocking)
- **MQTT Publish Interval**: 5 seconds
- **MQTT Subscribe Latency**: <100 ms
- **Alert Response Time**: <50 ms (from message to LED/buzzer)
- **DHT11 Sensor Lag**: Up to 2 seconds (sensor limitation)
- **Power Consumption**: ~200-250 mA at 5V

## Typical Operation Sequence

```
1. Power On
   → "Init Reseau..." on LCD
   → DHCP configuration (2-3 seconds)
   → MQTT connection attempt

2. Normal Operation (Loop)
   → Every 5 seconds:
      ├─ Read DHT11 temperature/humidity
      ├─ Read LDR light level
      ├─ Update LCD display
      └─ Publish JSON to salle/sensors
   → Continuously:
      ├─ Check MQTT for messages
      └─ Listen for alerts on salle/mouvement

3. On Motion Alert Received
   → Trigger 3-pulse LED/buzzer alert
   → Display red on LCD
   → Return to normal display after 1.3 seconds
   → Continue sensor publishing
```

## Power Management Notes

- **Idle Power**: ~100-150 mA (waiting for MQTT messages)
- **Active Power**: ~200-250 mA (sensor reading + publishing)
- **Alert Power**: ~300 mA (LED + buzzer at max output)
- **Supply**: 5V USB or barrel connector

## Future Enhancements

- Configurable alert patterns (pulse count, frequency, duration)
- Motion sensitivity threshold adjustment
- Temperature/humidity thresholds with automatic alerts
- Multiple alert sound frequencies
- Recording alert events with timestamps
- Integration with remote notification system
- Web interface for configuration
- Relay module integration for automated door/light control
