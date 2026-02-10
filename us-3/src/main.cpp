#include <Wire.h>
#include "rgb_lcd.h"
#include "Grove_Temperature_And_Humidity_Sensor.h"

#define DHTTYPE DHT11 // DHT 11
#define DHTPIN 2
#define LDRPIN A0 // Light Dependent Resistor on analog pin A0

#if defined(ARDUINO_ARCH_AVR)
#define debug Serial

#elif defined(ARDUINO_ARCH_SAMD) || defined(ARDUINO_ARCH_SAM)
#define debug SerialUSB
#else
#define debug Serial
#endif

DHT dht(DHTPIN, DHTTYPE);
rgb_lcd lcd;

const int colorR = 255;
const int colorG = 255;
const int colorB = 255;

void setup()
{
  debug.begin(9600);
  debug.println("DHT11 test!");

  dht.begin();

  // set up the LCD's number of columns and rows:
  lcd.begin(16, 2);

  lcd.setRGB(colorR, colorG, colorB);

  // Print a message to the LCD.
  lcd.print("hello, world!");

  delay(2000);

  lcd.clear();
}

void loop()
{
  // set the cursor to column 0, line 1
  // (note: line 1 is the second row, since counting begins with 0):
  // lcd.setCursor(0, 1);

  float temp_hum_val[2] = {0};
  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)

  // Read LDR value and convert to lux
  int ldrValue = analogRead(LDRPIN);
  // Calibrate these values based on your LDR and lighting conditions
  // Typical: dark = ~1023, bright = ~0 (inverse relationship)
  int lightLux = map(ldrValue, 0, 1023, 0, 10000); // maps to 0-10000 lux

  if (!dht.readTempAndHumidity(temp_hum_val))
  {
    // Display light level and temperature on LCD
    lcd.setCursor(0, 0);
    lcd.print("Lum: ");
    lcd.print(lightLux);
    lcd.print(" lux");

    lcd.setCursor(0, 1);
    lcd.print("Temp: ");
    lcd.print(temp_hum_val[1]);
    lcd.print(" *C");

    // Print all data to console
    debug.print("Humidity: ");
    debug.print(temp_hum_val[0]);
    debug.print(" %\t");
    debug.print("Temperature: ");
    debug.print(temp_hum_val[1]);
    debug.print(" *C\t");
    debug.print("Light Level: ");
    debug.print(lightLux);
    debug.println(" lux");
  }
  else
  {
    debug.println("Failed to get temperature and humidity value.");
  }

  delay(100);
}