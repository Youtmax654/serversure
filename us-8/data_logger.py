import sqlite3
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

# --- CONFIGURATION ---
MQTT_BROKER = "localhost"
DB_NAME = "dashboard/surveillance.db"

# Topics to listen to
TOPIC_SENSORS = "salle/sensors"   # From Arduino
TOPIC_MOTION = "salle/mouvement"  # From ESP32

# --- DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table for Environmental Data (Arduino)
    # Added 'humidity REAL'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity REAL,
            luminosity INTEGER
        )
    ''')
    
    # Table for Security Alerts (ESP32)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            alert_type TEXT,
            value REAL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized (with Humidity).")

# --- MQTT CALLBACKS ---

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker (rc: {rc})")
    client.subscribe([(TOPIC_SENSORS, 0), (TOPIC_MOTION, 0)])

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        topic = msg.topic
        data = json.loads(payload)
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # 1. Handle Arduino Data (Temp/Lux/Hum)
        if topic == TOPIC_SENSORS:
            # Expecting JSON: {"temp": 24.5, "hum": 50.0, "lux": 300}
            temp = data.get("temp")
            hum = data.get("hum")  # Get humidity
            lux = data.get("lux")
            
            # We check if temp and lux are present. 
            # Humidity is optional (if your sensor fails, it records None)
            if temp is not None:
                cursor.execute(
                    "INSERT INTO measurements (temperature, humidity, luminosity) VALUES (?, ?, ?)",
                    (temp, hum, lux)
                )
                print(f"📝 Saved Sensor Data: T={temp}°C, H={hum}%, L={lux}")

        # 2. Handle ESP32 Data (Motion)
        elif topic == TOPIC_MOTION:
            status = data.get("status")
            val = data.get("value")
            
            if status in ["ALERTE", "ALERT", "OK"]:
                cursor.execute(
                    "INSERT INTO alerts (alert_type, value) VALUES (?, ?)",
                    (status, val)
                )
                print(f"🚨 Saved Motion Status: {status} (Distance={val}cm)")

        conn.commit()
        conn.close()

    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {msg.topic}")
    except Exception as e:
        print(f"Error: {e}")

# --- MAIN LOOP ---
if __name__ == "__main__":
    init_db()
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    print("Connecting to MQTT...")
    client.connect(MQTT_BROKER, 1883, 60)
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nStopping Data Logger.")