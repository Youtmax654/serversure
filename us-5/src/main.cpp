#include <WiFi.h>
#include "Ultrasonic.h"
#include <PubSubClient.h>

// --- CONFIGURATION ---
const char *ssid = "rpi-serversure";
const char *password = "lc9dAcDY4J";
const char *mqtt_server = "10.42.0.1";

// Distance threshold (cm)
const int ALERT_VALUE = 50; 


 

// --- OBJECTS ---
WiFiClient espClient;
PubSubClient client(espClient);
Ultrasonic ultrasonic(4);

// --- VARIABLES ---
bool inAlertState = false;

void setup()
{
  Serial.begin(115200);
  delay(1000);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("\nConnecting");

  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(100);
  }

  Serial.println("\nConnected to the WiFi network");
  Serial.print("Local ESP32 IP: ");
  Serial.println(WiFi.localIP());

  client.setServer(mqtt_server, 1883);
}

void reconnect()
{
  while (!client.connected())
  {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32_Security_Ultrason"))
    {
      Serial.println("Connected!");
    }
    else
    {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5s");
      delay(5000);
    }
  }
}

void loop()
{
  if (!client.connected())
  {
    reconnect();
  }
  client.loop();

  // 1. Measure distance
  long RangeInCentimeters = ultrasonic.MeasureInCentimeters();

  Serial.print("Distance: ");
  Serial.print(RangeInCentimeters);
  Serial.println(" cm");

  // 2. Alert Logic (State-based)
  if (RangeInCentimeters > 0 && RangeInCentimeters < ALERT_VALUE)
  {
    if (!inAlertState)
    {
      Serial.println(">>> TRIGGER: SENDING ALERT <<<");
      
      String payload = "{\"status\": \"ALERT\", \"value\": " + String(RangeInCentimeters) + "}";
      client.publish("salle/mouvement", payload.c_str());
      
      inAlertState = true;
    }
  }
  else
  {
    if (inAlertState)
    {
      Serial.println(">>> RESTORE: SENDING OK <<<");
      
      String payload = "{\"status\": \"OK\", \"value\": " + String(RangeInCentimeters) + "}";
      client.publish("salle/mouvement", payload.c_str());
      
      inAlertState = false;
    }
  }

  delay(250); // Small delay for sensor stability
}