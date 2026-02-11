#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h> // A installer via le gestionnaire de bibliothèque
#include <Wire.h>
#include "rgb_lcd.h"
#include "Grove_Temperature_And_Humidity_Sensor.h"

// --- CONFIGURATION MATERIEL ---
#define DHTTYPE DHT11
#define DHTPIN 2
#define LDRPIN A0 // Light Dependent Resistor on analog pin A0

// --- CONFIGURATION RESEAU ---
byte mac[] = {0x90, 0xA2, 0xDA, 0x10, 0xDD, 0xF9};
IPAddress server(10, 160, 24, 211);

// --- OBJETS ---
DHT dht(DHTPIN, DHTTYPE);
rgb_lcd lcd;
EthernetClient ethClient;
PubSubClient client(ethClient);

// --- VARIABLES ---
const int colorR = 255;
const int colorG = 255;
const int colorB = 255;
long lastMsg = 0; // Pour gérer le temps sans delay()

// Macro pour le debug (gardée de ton code)
#if defined(ARDUINO_ARCH_AVR)
#define debug Serial
#elif defined(ARDUINO_ARCH_SAMD) || defined(ARDUINO_ARCH_SAM)
#define debug SerialUSB
#else
#define debug Serial
#endif

void setup()
{
  debug.begin(9600);
  debug.println("Demarrage System...");

  // 1. Init Capteurs & Ecran
  dht.begin();
  lcd.begin(16, 2);
  lcd.setRGB(colorR, colorG, colorB);
  lcd.print("Connexion reseau");

  // 2. Init Ethernet
  // On laisse le temps au shield de s'allumer
  delay(1000);

  if (Ethernet.begin(mac) == 0)
  {
    debug.println("Echec configuration DHCP");
    lcd.setRGB(255, 0, 0); // Rouge = Erreur
    lcd.setCursor(0, 1);
    lcd.print("Erreur DHCP");
    // Si pas de DHCP, on pourrait forcer une IP statique ici,
    // mais pour l'instant on bloque.
    while (true)
      ;
  }
  else
  {
    debug.print("IP attribuee : ");
    debug.println(Ethernet.localIP());
    lcd.setCursor(0, 1);
    lcd.print(Ethernet.localIP());
    delay(2000); // Juste pour lire l'IP
  }

  // 3. Config MQTT
  client.setServer(server, 1883);
  lcd.clear();
}

void reconnect()
{
  // Boucle jusqu'à la connexion au Broker MQTT
  while (!client.connected())
  {
    debug.print("Tentative connexion MQTT...");
    // ID Client unique
    if (client.connect("Arduino_DHT_Client"))
    {
      debug.println("Connecte !");
      lcd.setRGB(0, 255, 0); // Vert = Connecté
    }
    else
    {
      debug.print("Echec, rc=");
      debug.print(client.state());
      debug.println(" retry 5s");
      lcd.setRGB(255, 100, 0); // Orange = Tentative
      delay(5000);
    }
  }
}

void loop()
{
  // 1. Gestion de la connexion MQTT
  if (!client.connected())
  {
    reconnect();
  }
  client.loop(); // Important pour traiter les messages entrants/sortants

  // 2. Lecture et Envoi toutes les 5 secondes (NON BLOQUANT)
  long now = millis();
  if (now - lastMsg > 5000)
  {
    lastMsg = now;

    float temp_hum_val[2] = {0};

    // Read LDR value and convert to lux
    int ldrValue = analogRead(LDRPIN);
    // Calibrate these values based on your LDR and lighting conditions
    // Typical: dark = ~1023, bright = ~0 (inverse relationship)
    int lightLux = map(ldrValue, 0, 1023, 0, 10000); // maps to 0-10000 lux

    // Lecture du capteur
    if (!dht.readTempAndHumidity(temp_hum_val))
    {
      int humidity = temp_hum_val[0];
      int temperature = temp_hum_val[1];

      // Display light level and temperature on LCD
      lcd.setCursor(0, 0);
      lcd.print("Lum: ");
      lcd.print(lightLux);
      lcd.print(" lux");

      lcd.setCursor(0, 1);
      lcd.print("T: ");
      lcd.print(temperature);
      lcd.print("*C");

      lcd.setCursor(8, 1);
      lcd.print("H: ");
      lcd.print(humidity);
      lcd.print("%");

      // --- B. Envoi MQTT (JSON) ---
      // On construit le message : {"temp": 24.0, "hum": 50.0}
      String payload = "{\"temp\":";
      payload += temperature;
      payload += ", \"hum\":";
      payload += humidity;
      payload += ", \"lux\":";
      payload += lightLux;
      payload += "}";

      // Conversion en tableau de char pour la librairie MQTT
      char msgBuffer[100];
      payload.toCharArray(msgBuffer, 100);

      debug.print("Publish: ");
      debug.println(msgBuffer);

      // Publication sur le topic "salle/sensors"
      client.publish("salle/sensors", msgBuffer);
    }
    else
    {
      debug.println("Erreur lecture DHT");
      lcd.setCursor(0, 0);
      lcd.print("Erreur Capteur");
    }
  }
}