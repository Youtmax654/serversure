#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>
#include <Wire.h>
#include "Grove_Temperature_And_Humidity_Sensor.h"
#include "rgb_lcd.h"

// --- CONFIGURATION MATERIEL ---
#define DHTTYPE DHT11
#define DHTPIN 2
#define LDRPIN A0  // <--- AJOUT DU CAPTEUR DE LUMIERE
#define LED 6
#define BUZZER 3

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
long lastMsg = 0; 

#if defined(ARDUINO_ARCH_AVR)
#define debug Serial
#elif defined(ARDUINO_ARCH_SAMD) || defined(ARDUINO_ARCH_SAM)
#define debug SerialUSB
#else
#define debug Serial
#endif

// --- CALLBACK (Réception ALERTE) ---
void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) { message += (char)payload[i]; }

  if (message == "ALERTE") {
    lcd.setRGB(255, 0, 0); 
    for(int i = 0; i < 3; i++) {
      digitalWrite(LED, HIGH);
      tone(BUZZER, 1000);
      delay(300);
      digitalWrite(LED, LOW);
      noTone(BUZZER);
      delay(200);
    }
    lcd.setRGB(colorR, colorG, colorB); 
  }
}

// --- RECONNECT ---
void reconnect() {
  while (!client.connected()) {
    if (client.connect("Arduino_Multi_Station")) {
      client.subscribe("salle/mouvement");
      lcd.setRGB(0, 255, 0);
    } else {
      delay(5000);
    }
  }
}

void setup() {
  debug.begin(9600);
  pinMode(LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  dht.begin();
  lcd.begin(16, 2);
  lcd.setRGB(colorR, colorG, colorB);
  lcd.print("Init Reseau...");

  delay(1000);
  if (Ethernet.begin(mac) == 0) {
    lcd.setRGB(255, 0, 0);
    while (true);
  }
  
  client.setServer(server, 1883);
  client.setCallback(callback);
  lcd.clear();
}

const double k = 5.0 / 1024;
const double R2 = 10000;
const double B = 1.3 * pow(10.0, 7);
const double m = -1.4;

double light_intensity(int RawADC0) {
  double V2 = k * RawADC0;
  double R1 = (5.0 / V2 - 1) * R2;
  double lux = B * pow(R1, m);
  return lux;
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  long now = millis();
  if (now - lastMsg > 5000) {
    lastMsg = now;

    float temp_hum_val[2] = {0};
    
    // --- LECTURE LUMIERE ---
    int ldrValue = analogRead(LDRPIN);
    int lightLux = light_intensity(ldrValue);

    if (!dht.readTempAndHumidity(temp_hum_val)) {
      float humidity = temp_hum_val[0];
      float temperature = temp_hum_val[1];

      // --- AFFICHAGE LCD ---
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Lum: "); lcd.print(lightLux); lcd.print(" lux"); // <--- LA LUMIERE EST ICI
      lcd.setCursor(0, 1);
      lcd.print("T:"); lcd.print(temperature); lcd.print("C H:"); lcd.print(humidity); lcd.print("%");

      // --- ENVOI MQTT ---
      String payload = "{\"temp\":";
      payload += temperature;
      payload += ", \"hum\":";
      payload += humidity;
      payload += ", \"lux\":";
      payload += lightLux;
      payload += "}";

      char msgBuffer[100];
      payload.toCharArray(msgBuffer, 100);
      client.publish("salle/sensors", msgBuffer);
    }
  }
}