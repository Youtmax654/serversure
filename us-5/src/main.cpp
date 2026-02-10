#include <WiFi.h>
#include "Ultrasonic.h"
#include <PubSubClient.h>

const char *ssid = "rpi-serversure";
const char *password = "lc9dAcDY4J";

const char *mqtt_server = "10.42.0.1";

const int ALERT_VALUE = 50;

WiFiClient espClient;
PubSubClient client(espClient);

Ultrasonic ultrasonic(4);

void setup()
{
  Serial.begin(115200);
  delay(1000);

  WiFi.mode(WIFI_STA); // Optional
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
  // Boucle jusqu'à la reconnexion
  while (!client.connected())
  {
    Serial.print("Tentative de connexion MQTT...");
    // ID Client unique requis
    if (client.connect("ESP32_Security_Ultrason"))
    {
      Serial.println("Connecté !");
    }
    else
    {
      Serial.print("Echec, rc=");
      Serial.print(client.state());
      Serial.println(" nouvel essai dans 5s");
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

  long RangeInCentimeters = ultrasonic.MeasureInCentimeters();

  Serial.print("The distance of obstacles in front is: ");
  Serial.print(RangeInCentimeters);
  Serial.println(" cm");

  if (RangeInCentimeters > 0 && RangeInCentimeters < ALERT_VALUE)
  {
    Serial.print("ALERT");

    client.publish("salle/mouvement", "ALERTE");
  }

  delay(250);
}