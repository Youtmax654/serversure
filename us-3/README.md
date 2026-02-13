# Environmental Monitoring System (US-3)

## Description

This project implements an environmental monitoring system using an Arduino Uno microcontroller. It reads temperature, humidity, and ambient light levels, displaying the data on a 16x2 RGB LCD screen and transmitting it to the serial console.

## Features

- **Temperature & Humidity Monitoring**: Reads data from a DHT11 sensor
- **Light Level Detection**: Measures ambient light using an LDR (Light Dependent Resistor)
- **Real-time Display**: Shows temperature and light level on a 16x2 RGB LCD screen
- **Serial Logging**: Outputs all sensor readings to the serial port for debugging and monitoring

## Hardware Requirements

- **Microcontroller**: Arduino Uno
- **Temperature & Humidity Sensor**: Grove DHT11 (connected to pin 2)
- **Light Sensor**: LDR (Light Dependent Resistor) on analog pin A0
- **Display**: Grove LCD RGB Backlight (16x2 characters, I2C interface)
- **Connection**: I2C bus for LCD communication

## Dependencies

This project uses the following libraries (managed via PlatformIO):

- `Grove - LCD RGB Backlight` (v1.0.2+)
- `Grove Temperature And Humidity Sensor` (v2.0.2+)

## Installation

1. Ensure PlatformIO is installed in your IDE (VS Code or compatible)
2. Open the project folder in PlatformIO
3. The required libraries will be installed automatically based on `platformio.ini`
4. Upload the firmware to your Arduino Uno

## Usage

1. Connect all sensors to the Arduino according to the pin configuration:
   - DHT11 to pin 2
   - LDR to analog pin A0
   - LCD to I2C bus (SDA/SCL)

2. Upload the sketch to the Arduino Uno

3. Open the Serial Monitor at 9600 baud to view sensor readings

4. The LCD will display:
   - **Line 1**: Light level in lux (0-10000 scale)
   - **Line 2**: Temperature in °C

## Data Format

Serial output format:
```
Humidity: [value] %    Temperature: [value] °C    Light Level: [value] lux
```

## Calibration Notes

- **LDR**: The light-to-lux mapping (0-10000 lux) should be calibrated based on your specific sensor and lighting environment
- **DHT11**: Sensor readings take approximately 250ms and may be up to 2 seconds old due to the sensor's slow response time

## Troubleshooting

- **No LCD display**: Check I2C connection and ensure the Grove LCD library is properly installed
- **DHT11 errors**: Verify the sensor connection and check that pin 2 is correctly configured
- **Inaccurate light readings**: Recalibrate the LDR mapping values based on your environment
