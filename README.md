# ServerSure - IoT Security & Monitoring System

## 🏢 Project Overview

**ServerSure** is a comprehensive IoT security and environmental monitoring system designed for real-time surveillance, threat detection, and environmental data logging. It integrates multiple hardware platforms (Arduino, ESP32, Raspberry Pi) with a centralized MQTT broker and data persistence layer to provide complete facility monitoring capabilities.

The system is modular and scalable, allowing individual components to operate independently while sharing data through MQTT protocols for a unified monitoring experience.

## 🎯 Key Features

- **Real-Time Environmental Monitoring**: Temperature, humidity, and light level tracking
- **Motion & Intrusion Detection**: Ultrasonic sensor-based proximity alerts
- **Automated Video Surveillance**: Camera triggers on motion detection events
- **Centralized Data Logging**: All sensor and alert data stored in SQLite database
- **MQTT-Based Communication**: Standardized pub/sub architecture for scalability
- **Local and Remote Monitoring**: Web dashboard for real-time visualization
- **Audio-Visual Alerts**: LED and buzzer notifications on threat detection
- **Headless Operation**: Designed for unattended, continuous monitoring

## 📚 Project Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                      ServerSure System                        │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │   US-3 & US-4    │  │   US-5 & US-11   │                   │
│  │  Environmental   │  │  Motion Detection│                   │
│  │  Monitoring      │  │  & Local Alerts  │                   │
│  │  (Arduino Uno)   │  │  (ESP32 + Ard.)  │                   │
│  └────────┬─────────┘  └────────┬─────────┘                   │
│           │                     │                             │
│           │ MQTT                │ MQTT                        │
│           │ salle/sensors       │ salle/mouvement             │
│           │                     │                             │
│           └──────────┬──────────┘                             │
│                      │                                        │
│              ┌───────▼──────────┐                             │
│              │  MQTT Broker     │                             │
│              │ (10.160.24.211)  │                             │
│              └───────┬──────────┘                             │
│                      │                                        │
│      ┌───────────────┼───────────────┐                        │
│      │               │               │                        │
│  ┌───▼──┐        ┌───▼──┐       ┌────▼───┐                    │
│  │US-6  │        │US-8  │       │US-11   │                    │
│  │Camera│        │Logger │       │Multi   │                   │
│  │      │        │(SQLite)      │Station │                    │
│  └──────┘        └───────┘       └────────┘                   │
│                      │                                        │
│              ┌───────▼──────────┐                             │
│              │   Dashboard      │                             │
│              │   (React/Vite)   │                             │
│              └──────────────────┘                             │
│                                                               │
└───────────────────────────────────────────────────────────────
```

## 📦 System Components

### Hardware Modules

| Component | US ID | Platform | Purpose |
|-----------|-------|----------|---------|
| **Environmental Monitor** | US-3 | Arduino Uno | Temperature, humidity, light monitoring |
| **MQTT Environmental Gateway** | US-4 | Arduino Uno + Ethernet | Publish sensor data to MQTT broker |
| **Motion Detection Sensor** | US-5 | ESP32 | Ultrasonic-based intrusion detection |
| **Security Camera** | US-6 | Raspberry Pi | Automated photo capture on motion |
| **Data Logger** | US-8 | Raspberry Pi/Server | SQLite database for all events |
| **Multi-Function Station** | US-11 | Arduino Uno + Ethernet | Monitoring + Alert response |

### Network Infrastructure

- **MQTT Broker**: Central message hub at `10.160.24.211:1883`
- **Database**: SQLite (`surveillance.db`) on local server
- **Dashboard**: React/Vite web application for visualization
- **API Server**: Python backend for data access (api/)

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Node.js 16+ (for dashboard)
- MQTT Broker running and accessible
- PlatformIO for Arduino/ESP32 firmware
- Raspberry Pi with camera module (for US-6)

## 📡 MQTT Topics

### Published Topics

| Topic | Source | Payload | Frequency |
|-------|--------|---------|-----------|
| `salle/sensors` | US-4, US-11 | `{"temp": 23.5, "hum": 55, "lux": 3200}` | Every 5s |
| `salle/mouvement` | US-5 | `{"status": "ALERT", "value": 35}` | On event |

### Subscribed Topics

| Topic | Subscriber | Action |
|-------|-----------|--------|
| `salle/mouvement` | US-6 (Camera) | Trigger photo capture |
| `salle/mouvement` | US-11 (Station) | Activate LED/buzzer alert |
| `salle/sensors` | US-8 (Logger) | Store in database |

## 📋 Detailed Documentation

Each component has detailed documentation in its respective folder:

### Sensor & Data Collection
- **[US-3: Environmental Monitoring System](us-3/README.md)** - DHT11 + LDR temperature, humidity, light monitoring
- **[US-4: MQTT Environmental Gateway](us-4/README.md)** - Ethernet-enabled sensor data publisher
- **[US-5: Motion Detection System](us-5/README.md)** - ESP32 ultrasonic motion sensor with WiFi

### Alert & Response Systems
- **[US-6: Security Camera System](us-6/README.md)** - Automated photo capture on motion detection
- **[US-11: Multi-Function Station](us-11/README.md)** - Combined monitoring + alert response (LED/buzzer)

### Data Management & Visualization
- **[US-8: Data Logger System](us-8/README.md)** - Centralized SQLite database for all events
- **[Dashboard Application](app/README.md)** - React/Vite web interface
- **[API Server](api/README.md)** - Python backend for data access

## 🔧 Configuration

### Global MQTT Configuration

```
MQTT Broker Address: 10.160.24.211
MQTT Port: 1883
MQTT Protocol Version: 3.1.1
```

### Arduino Network Configuration

```
MAC Address: 90:A2:DA:10:DD:F9
MQTT Server: 10.160.24.211:1883
DHCP: Enabled
```

### Raspberry Pi Configuration

```
MQTT Broker: localhost or 10.160.24.211
Database: dashboard/surveillance.db
```

## 🐛 Troubleshooting

### MQTT Broker Not Responding

```bash
# Test MQTT broker connectivity
telnet 10.160.24.211 1883

# Subscribe to topics for debugging
mosquitto_sub -h 10.160.24.211 -t "salle/#"
```

### Database Connection Error

```bash
# Check database file exists
ls -la dashboard/surveillance.db

# Check API server is running
curl http://localhost:5000/api/sensors

# Verify database has records
sqlite3 dashboard/surveillance.db "SELECT COUNT(*) FROM measurements;"
```


## 🔐 Security Considerations
1. SSH Server Security
We identified the main vulnerabilities and how to "harden" remote access:

Eliminate Passwords: Switch exclusively to SSH Keys (Ed25519) to stop brute-force attacks.

Restrict Root Access: Disable direct root login (PermitRootLogin no) to limit an intruder's immediate power.

Software Hygiene: Disable old protocols (SSH-1) and keep OpenSSH updated to avoid critical vulnerabilities like RegreSSHion.

Defense Tools: Use Fail2Ban to block suspicious IPs and consider changing the default port (22) to reduce automated bot noise.

2. MQTT Broker Security
The MQTT protocol is efficient but highly vulnerable if left with default settings:

Mandatory Authentication: Always disable anonymous access (allow_anonymous false).

Access Control Lists (ACLs): Restrict users to specific topics so a compromised sensor cannot read or control the entire system.

Encryption: Use MQTTS (TLS) to prevent messages from being intercepted in plain text over the network.

3. Network Architecture & REST API (Raspberry Pi)
Since your RPI exposes a REST API via Wi-Fi, isolation is critical:

Network Segmentation: Separate your flows. If the MQTT broker is only used internally by the RPI, bind it to the local interface (127.0.0.1) so it isn't reachable from the Wi-Fi.

Reverse Proxy (Nginx): Place a proxy in front of your REST API to handle SSL/TLS encryption, filter malicious requests, and centralize authentication.

The Wi-Fi Risk: Since the Wi-Fi is the entry point for users, the proxy acts as a "shield" between the public-facing Wi-Fi and your critical internal services.

Core Strategy: Focus on Defense in Depth—combining strong authentication (Keys/Passphrases), traffic encryption (TLS), and network isolation (Proxy/Local Interfaces).

## 🚦 System Status Dashboard

Access the web dashboard at `http://localhost:3000` to view:

- Real-time environmental data (temperature, humidity, light)
- Motion detection history with timestamps
- Camera snapshots and event timeline
- Database statistics and storage usage
- System health and connectivity status

## 🎓 Development Setup

### Project Structure

```
serversure/
├── us-3/               # Environmental Monitor (Arduino)
│   ├── src/main.cpp
│   └── platformio.ini
│
├── us-4/               # MQTT Environmental Gateway
│   ├── src/main.cpp
│   └── platformio.ini
│
├── us-5/               # Motion Detection (ESP32)
│   ├── src/main.cpp
│   └── platformio.ini
│
├── us-6/               # Security Camera (Raspberry Pi)
│   ├── security_cam.py
│   └── README.md
│
├── us-8/               # Data Logger (Server)
│   ├── data_logger.py
│   └── README.md
│
├── us-11/              # Multi-Function Station (Arduino)
│   ├── src/main.cpp
│   └── platformio.ini
│
├── app/                # Dashboard (React/Vite)
│   ├── src/
│   ├── package.json
│   └── README.md
│
├── api/                # Backend API (Python)
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
│
└── README.md           # This file
```
## 📞 Support & Documentation

- **Technical Issues**: Check individual component READMEs in each US folder
- **MQTT Debugging**: Use `mosquitto_sub` and `mosquitto_pub` tools
- **Database Queries**: Use SQLite command-line shell with provided schema
- **Hardware Issues**: Consult component-specific documentation
