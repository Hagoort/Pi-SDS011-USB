# Connects Raspberry Pi to SDS011 air quality sensor via USB and sends results to sensor.community
# Version 20230204

import time
import serial
import requests
import datetime
import json

# Open serial connection to sensor
ser = serial.Serial('/dev/ttyUSB0', baudrate=9600)

# Your sensor's coordinates
latitude = 12.34567890123
longitude = 1.23456789012

# Format the coordinates as a string
location = str(latitude) + "," + str(longitude)

# Your different sensor ID's
UID = "raspi-1234"
hashtag = 12345
sensor_id = 12345

while True:
    # Put sensor in measurement mode and turn fan on
    ser.write(b'\xAA\xB4\x06\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x06\xAB')
    print("**********************************")
    print("Putting sensor in measurement mode")

    # Wait 30 seconds for sensor to warm up with fan on
    print("Waiting 30 seconds for the sensor to warm up with the fan on")
    time.sleep(30)

    # Start reading data from the sensor
    data = ser.read(10)

    # Extract high and low bytes for PM2.5 and PM10 from data
    pm25_low = data[2]
    pm25_high = data[3]
    pm10_low = data[4]
    pm10_high = data[5]

    # Calculate PM2.5 and PM10 values
    pm25 = ((pm25_high * 256) + pm25_low) / 10
    pm10 = ((pm10_high * 256) + pm10_low) / 10

    # Print results
    print("PM2.5: ", pm25, "ug/m^3")
    print("PM10: ", pm10, "ug/m^3")

    # Print timestamp
    now = datetime.datetime.now()
    print("Timestamp: ", now)

    # Put sensor in sleeping mode and turn fan off to extend it's lifetime
    ser.write(b'\xAA\xB4\x06\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x05\xAB')
    print("Putting sensor in sleep mode and turning off fan")

    # Send data to sensor community server
    api_endpoint = "https://api.sensor.community/v1/push-sensor-data/"
    data = {
        "id": hashtag,
        "sensordatavalues": [
            {
                "value_type": "P1",
                "value": pm10
            },
            {
                "value_type": "P2",
                "value": pm25
            }
        ],
        "location": location,
        "sensor_id": sensor_id,
        "timestamp": now.isoformat()
    }

    auth = {
    "X-Sensor": UID
    }

    # Send data to API and print response
    response = requests.post(api_endpoint, json=data, headers=auth)
    print("Response:", response.text)

    # Take reading every 4m:30s (includes warm up)
    print("Waiting 4 minutes for next cycle")
    time.sleep(240)

