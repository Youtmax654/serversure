import paho.mqtt.client as mqtt
import os
import json
import time
from datetime import datetime

# --- CONFIGURATION ---
MQTT_BROKER = "localhost"
MQTT_TOPIC = "salle/mouvement"
PHOTO_DIR = "/home/traps/Scripts/dashboard/surveillance_photos"

# Create directory if it doesn't exist
if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

# Callback triggered when a message is received
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        
        # # Check if status is ALERT (matching the ESP32 message)
        if payload == "ALERTE":
            print(f"🚨 Motion detected!")
            take_photo()


    except Exception as e:
        print(f"Error reading message: {e}")

def take_photo():
    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{PHOTO_DIR}/capture_{timestamp}.jpg"
    
    print(f"📸 Taking photo: {filename}")
    
    # System command to take the picture (Bookworm uses rpicam-jpeg)
    # -t 1: minimal preview time
    # --nopreview: essential for headless mode (no monitor)
    command = f"rpicam-jpeg -o {filename} -t 1 --width 1024 --height 768 --nopreview"
    
    # Execute command
    os.system(command)
    print("✅ Photo saved.")

# --- MQTT INITIALIZATION ---
client = mqtt.Client()
client.on_message = on_message

print(f"Connecting to broker {MQTT_BROKER}...")
client.connect(MQTT_BROKER, 1883, 60)

print(f"Subscribing to topic {MQTT_TOPIC}...")
client.subscribe(MQTT_TOPIC)

print("📷 Surveillance System ACTIVE. Waiting for motion...")
client.loop_forever()