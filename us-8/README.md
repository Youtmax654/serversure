# Data Logger System (US-8)

## Description

This project implements a centralized data logging system that aggregates sensor data and security alerts from multiple IoT devices into a SQLite database. The system listens to MQTT topics from environmental sensors (US-4: Temperature/Humidity/Light) and motion detection systems (US-5: Ultrasonic Sensor), stores all data with precise timestamps, and provides a historical record for analysis, reporting, and auditing purposes.

## Features

- **Multi-Topic MQTT Subscription**: Simultaneously listens to environmental sensors and motion alerts
- **Dual-Table Database**: Separate tables for measurements (environmental) and alerts (security)
- **Automatic Timestamping**: All records include server-side timestamps
- **Data Validation**: JSON parsing with error handling for corrupted messages
- **Flexible Schema**: Stores temperature, humidity, luminosity, motion status, and distance values
- **Persistent Storage**: SQLite database for reliable local data storage
- **Graceful Shutdown**: Handles interruption signals cleanly
- **Comprehensive Logging**: Console output for real-time monitoring

## System Requirements

### Hardware
- **Server Platform**: Raspberry Pi, Linux Server, or any machine with Python 3.7+
- **Storage**: SQLite database on local or networked filesystem
- **Network**: Connection to MQTT broker

### Software
- **Python**: 3.7 or higher
- **Database**: SQLite3 (built-in with Python)
- **MQTT Broker**: Accessible at configured address
- **Operating System**: Linux/macOS/Windows with Python support

## Dependencies

Install required Python packages:
```bash
pip install paho-mqtt
```

## Installation

1. **Clone or copy the project**:
   ```bash
   git clone <repository-url>
   cd us-8
   ```

2. **Install dependencies**:
   ```bash
   pip install paho-mqtt
   ```

3. **Create database directory** (if not using default):
   ```bash
   mkdir -p dashboard
   chmod 744 dashboard
   ```

4. **Update configuration** in `data_logger.py`:
   ```python
   MQTT_BROKER = "your-mqtt-broker-ip"
   DB_NAME = "path/to/surveillance.db"
   ```

5. **Run the data logger**:
   ```bash
   python3 data_logger.py
   ```

## Configuration

### MQTT Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MQTT_BROKER` | `localhost` | IP address or hostname of MQTT broker |
| `MQTT_PORT` | `1883` | MQTT broker port (hardcoded) |
| `TOPIC_SENSORS` | `salle/sensors` | Topic for environmental data (US-4) |
| `TOPIC_MOTION` | `salle/mouvement` | Topic for motion alerts (US-5) |

### Database Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `DB_NAME` | `dashboard/surveillance.db` | SQLite database file path |

## Database Schema

### Table: `measurements`

Stores environmental sensor data from US-4 (Arduino with Temperature/Humidity/Light sensors).

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key, auto-incremented |
| `timestamp` | DATETIME | When the record was saved (server time) |
| `temperature` | REAL | Temperature in °C |
| `humidity` | REAL | Relative humidity in % |
| `luminosity` | INTEGER | Light level in lux |

**Example Record**:
```sql
id: 1
timestamp: 2026-02-13 14:25:30
temperature: 23.5
humidity: 55.0
luminosity: 3200
```

### Table: `alerts`

Stores security alerts from US-5 (ESP32 with Ultrasonic Motion Sensor).

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key, auto-incremented |
| `timestamp` | DATETIME | When the alert was received |
| `alert_type` | TEXT | Status: `ALERT`, `ALERTE`, or `OK` |
| `value` | REAL | Distance measured in centimeters |

**Example Record**:
```sql
id: 1
timestamp: 2026-02-13 14:25:32
alert_type: ALERT
value: 35.5
```

## Usage

### Starting the Data Logger

**Manual Start**:
```bash
python3 data_logger.py
```

**With Output Logging to File**:
```bash
python3 data_logger.py > data_logger.log 2>&1 &
```

**As a Background Service**:
```bash
nohup python3 data_logger.py > data_logger.log 2>&1 &
```

**As a Systemd Service**:
Create `/etc/systemd/system/data-logger.service`:
```ini
[Unit]
Description=IoT Data Logger
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/us-8
ExecStart=/usr/bin/python3 /home/pi/us-8/data_logger.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable and start:
```bash
sudo systemctl enable data-logger.service
sudo systemctl start data-logger.service
```

### Expected Output

```
✅ Database initialized (with Humidity).
Connecting to MQTT...
Connected to MQTT Broker (rc: 0)
📝 Saved Sensor Data: T=23.5°C, H=55.0%, L=3200
🚨 Saved Motion Status: ALERT (Distance=35cm)
📝 Saved Sensor Data: T=23.6°C, H=54.8%, L=3250
🚨 Saved Motion Status: OK (Distance=120cm)
```

## MQTT Message Format

### Environmental Sensors (US-4)

**Topic**: `salle/sensors`

**Expected Payload**:
```json
{"temp": 23.5, "hum": 55.0, "lux": 3200}
```

**Mapping**:
- `temp` → `measurements.temperature`
- `hum` → `measurements.humidity`
- `lux` → `measurements.luminosity`

### Motion Alerts (US-5)

**Topic**: `salle/mouvement`

**Expected Payload**:
```json
{"status": "ALERT", "value": 35}
```

or

```json
{"status": "OK", "value": 120}
```

**Mapping**:
- `status` → `alerts.alert_type` (must be ALERT, ALERTE, or OK)
- `value` → `alerts.value` (distance in cm)

## Data Access & Querying

### Using SQLite Command Line

```bash
sqlite3 dashboard/surveillance.db
```

### View Recent Measurements

```sql
SELECT * FROM measurements 
ORDER BY timestamp DESC 
LIMIT 10;
```

### View Recent Alerts

```sql
SELECT * FROM alerts 
ORDER BY timestamp DESC 
LIMIT 10;
```

### Export Data to CSV

```bash
sqlite3 -header -csv dashboard/surveillance.db \
  "SELECT * FROM measurements" > measurements_export.csv
```

### Get Statistics

```sql
-- Average temperature over last 24 hours
SELECT AVG(temperature) as avg_temp 
FROM measurements 
WHERE timestamp > datetime('now', '-1 day');

-- Count of ALERT events
SELECT COUNT(*) as alert_count 
FROM alerts 
WHERE alert_type = 'ALERT';

-- All motion events with timestamp
SELECT timestamp, value FROM alerts 
WHERE alert_type IN ('ALERT', 'ALERTE') 
ORDER BY timestamp DESC;
```

## Integration Architecture

```
┌──────────────────────┐
│  Arduino Sensor      │
│  (Temperature/       │
│   Humidity/Light)    │
│  (US-4)              │
└──────────┬───────────┘
           │ MQTT
           │ salle/sensors
           │
┌──────────▼──────────────────┐
│   MQTT Broker                │
│   (localhost:1883)           │
└──────────┬───────────────────┘
           │
┌──────────┼──────────────────┐
│          │                  │
│          │                  │
│   ┌──────▼────────┐  ┌──────▼────────┐
│   │   Dashboard   │  │   Data Logger │
│   │             │  │   (US-8)       │
│   │   API       │  │   SQLite DB    │
│   └───────────────┘  └──────┬────────┘
│                             │
│                             ▼
│                      surveillance.db
│
│  ┌────────────────────────────────────────┐
│  │   From ESP32                           │
│  │   Motion Detection                     │
│  │   (US-5)                              │
│  └────────┬─────────────────────────────┘
│           │ MQTT
│           │ salle/mouvement
│           │
└───────────┴──────────────────────────────
```

## Data Retention & Management

### Database Size Estimation

- **Per environmental measurement**: ~100 bytes (with timestamp)
- **Per motion alert**: ~100 bytes (with timestamp)
- **Daily estimate** (1 measurement every 5 seconds, 1 alert per minute):
  - Measurements: ~17 KB/day
  - Alerts: ~1.4 KB/day
  - **Total**: ~20 KB/day (~600 KB/month)

### Automatic Cleanup Strategy

Add a cron job to archive old data:

```bash
# Archive measurements older than 90 days weekly
0 2 * * 0 sqlite3 /path/to/surveillance.db \
  "DELETE FROM measurements WHERE timestamp < datetime('now', '-90 days');"

# Archive alerts older than 365 days annually
0 3 1 * * sqlite3 /path/to/surveillance.db \
  "DELETE FROM alerts WHERE timestamp < datetime('now', '-365 days');"
```

## Troubleshooting

| Issue | Symptom | Solution |
|-------|---------|----------|
| MQTT connection fails | "Connecting to MQTT..." hangs | Verify broker IP, check network connectivity |
| Database locked | SQLite error on startup | Close other DB connections, ensure single logger instance |
| Messages not logged | No output from sensors/motion | Verify MQTT topics match, check message format is valid JSON |
| Disk space issues | Database file grows rapidly | Implement data archival, check message frequency |
| JSON decode errors | Error messages for sensor data | Verify MQTT payloads are valid JSON format |

## Performance Considerations

- **Write Performance**: ~1000 inserts/second (SQLite)
- **Read Performance**: Indexed by timestamp for fast queries
- **Memory Usage**: ~50 MB (persistent connection to MQTT broker)
- **CPU Usage**: <5% idle, spikes to 10-15% during data writes

## Security Considerations

1. **MQTT Authentication**: Use username/password on production brokers
2. **Database Access**: Restrict read access to authorized users
3. **Network**: Use VPN or firewall when logging remote sensors
4. **Backups**: Regular backup of surveillance.db file

## Integration with Other Components

Works seamlessly with:

- **US-4 (Environmental Sensors)**: Sources temperature/humidity/light data
- **US-5 (Motion Detection)**: Sources motion alerts
- **Dashboard Application**: Can query this database for statistics and reporting

## Future Enhancements

- InfluxDB or TimescaleDB integration for advanced analytics
- Data visualization dashboards
- Automated alerts based on threshold violations
- Data export/reporting functionality
- API endpoint for remote data access
- Data compression for long-term archival
- Real-time data streaming to external systems
