# IoT Surveillance API

A robust FastAPI application for monitoring server room conditions (Temperature, Humidity, Luminosity) and detecting intrusions on a Raspberry Pi.

## Features

- ✅ FastAPI with automatic interactive API documentation (Swagger UI)
- ✅ SQLite database integration (read-only from existing `surveillance.db`)
- ✅ CORS enabled for all origins (compatible with React frontends)
- ✅ Static file serving for surveillance photos
- ✅ Pydantic model validation for all responses
- ✅ Comprehensive error handling
- ✅ Health check endpoint

## Prerequisites

- Python 3.8+
- SQLite3 (usually included with Python)
- Existing `surveillance.db` file with populated `measurements` and `alerts` tables

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure your database exists:**
   - Place `surveillance.db` in the same directory as `api_rest.py`
   - Database should have tables: `measurements` and `alerts`

3. **Create the photos directory (optional):**
   ```bash
   mkdir -p /home/admin/surveillance_photos
   ```

## Running the Application

### Development Mode (with auto-reload):
```bash
python api_rest.py
```

### Production Mode:
```bash
uvicorn api_rest:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://<raspberry-pi-ip>:8000`

## API Documentation

### Interactive Swagger UI
Visit: `http://<raspberry-pi-ip>:8000/docs`

### Available Endpoints

#### 1. **Get Latest Measurement**
```
GET /api/sensors/last
```
Returns the most recent sensor reading.

**Response (200 OK):**
```json
{
  "timestamp": "2026-02-11 15:30:45",
  "temperature": 22.5,
  "humidity": 65.0,
  "luminosity": 450
}
```

**Response (404 Not Found):**
```json
{
  "detail": "No measurements found in database"
}
```

---

#### 2. **Get Measurement History**
```
GET /api/sensors/history?limit=20
```
Returns the last N sensor measurements.

**Query Parameters:**
- `limit` (int, default=20, min=1, max=1000): Number of measurements to retrieve

**Response (200 OK):**
```json
{
  "count": 3,
  "measurements": [
    {
      "timestamp": "2026-02-11 15:30:45",
      "temperature": 22.5,
      "humidity": 65.0,
      "luminosity": 450
    },
    {
      "timestamp": "2026-02-11 15:25:40",
      "temperature": 22.3,
      "humidity": 64.8,
      "luminosity": 445
    }
  ]
}
```

---

#### 3. **Get Alerts**
```
GET /api/alerts?limit=10
```
Returns the last N system alerts.

**Query Parameters:**
- `limit` (int, default=10, min=1, max=1000): Number of alerts to retrieve

**Response (200 OK):**
```json
{
  "count": 2,
  "alerts": [
    {
      "timestamp": "2026-02-11 14:22:10",
      "alert_type": "motion_detected",
      "value": "intrusion_detected"
    }
  ]
}
```

---

#### 4. **Serve Photos**
```
GET /photos/{filename}
```
Returns a specific image file from `/home/admin/surveillance_photos`.

**Example:**
- `GET /photos/motion_2026_02_11_14_22_10.jpg`

---

#### 5. **Health Check**
```
GET /health
```
Verifies API and database are operational.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-02-11T15:35:20.123456"
}
```

---

#### 6. **API Info**
```
GET /
```
Returns basic API information and available endpoints.

---

## Database Schema (Read-Only)

### `measurements` Table
```
id (INTEGER PRIMARY KEY)
timestamp (TEXT)
temperature (REAL)
humidity (REAL)
luminosity (INTEGER)
```

### `alerts` Table
```
id (INTEGER PRIMARY KEY)
timestamp (TEXT)
alert_status (TEXT)
value (TEXT)
```

## Frontend Integration

### Example with React/Axios:
```javascript
import axios from 'axios';

const API_BASE = 'http://192.168.1.100:8000';

// Get latest measurement
const getLatestMeasurement = async () => {
  const response = await axios.get(`${API_BASE}/api/sensors/last`);
  return response.data;
};

// Get measurement history
const getMeasurementHistory = async (limit = 50) => {
  const response = await axios.get(`${API_BASE}/api/sensors/history`, {
    params: { limit }
  });
  return response.data;
};

// Get alerts
const getAlerts = async (limit = 20) => {
  const response = await axios.get(`${API_BASE}/api/alerts`, {
    params: { limit }
  });
  return response.data;
};
```

## Troubleshooting

### Database file not found
- Ensure `surveillance.db` exists in the same directory as `main.py`
- Check file permissions: `chmod 644 surveillance.db`

### Photos directory not found
- The API will warn but continue to work
- Create the directory: `sudo mkdir -p /home/admin/surveillance_photos`
- Ensure the application has read permissions

### API not accessible from other machines
- Verify firewall settings: `sudo ufw allow 8000`
- Check Raspberry Pi IP: `hostname -I`
- Test locally first: `curl http://localhost:8000`

### Port already in use
- Change port in `main.py` or use: `uvicorn main:app --port 8001`

## Performance Notes

- Database is accessed fresh for each request (no connection pooling needed for light loads)
- For high-traffic scenarios, consider adding connection pooling or caching
- The `limit` parameter is capped at 1000 to prevent excessive memory usage

## License

This project is part of the IOT Surveillance system.
