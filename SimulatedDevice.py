# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import random
import time
from bs4 import BeautifulSoup as bs
import requests

USR_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
LANG = "en-AU,en;q=0.5"

# Using the Python Device SDK for IoT Hub:
#   https://github.com/Azure/azure-iot-sdk-python
# The sample connects to a device-specific MQTT endpoint on your IoT Hub.
from azure.iot.device import IoTHubDeviceClient, Message

# The device connection string to authenticate the device with your IoT hub.
# Using the Azure CLI:
# az iot hub device-identity show-connection-string --hub-name {YourIoTHubName} --device-id MyNodeDevice --output table
CONNECTION_STRING = "HostName=msa-learn-iot.azure-devices.net;DeviceId=MyPythonDevice;SharedAccessKey=Neur/u5E1oMet4cm3Q4GQ3sK47UDsGQZ2a+zWphMjN4="

# Define the JSON message to send to IoT Hub.
MSG_TXT = '{{ "temperature": {temperature},"precipitation": {precipitation},"humidity": {humidity},"wind": {wind},}}'

# Location to get Sydney weather data
URL = "https://www.google.com/search?q=weather+sydney"

def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client

# Web scraper to collect Sydney weather data from google weather
def get_weather_data(url):
    session = requests.Session()
    session.headers['User-Agent'] = USR_AGENT
    session.headers['Accept-Language'] = LANG
    session.headers['Content-Language'] = LANG
    page = session.get(url)
    soup = bs(page.text, "html.parser")
    # Store extracted weather data in dictionary
    data = {}
    # Get current temperature
    data['temperature'] = soup.find("span", attrs={"id": "wob_tm"}).text
    # Get current precipitation
    data['precipitation'] = soup.find("span", attrs={"id": "wob_pp"}).text
    # Get current humidity
    data['humidity'] = soup.find("span", attrs={"id": "wob_hm"}).text
    # Get current wind speed
    data['wind'] = soup.find("span", attrs={"id": "wob_ws"}).text
    return data

def send_weather_data():
    try:
        client = iothub_client_init()
        print ( "IoT Hub device sending periodic messages, press Ctrl-C to exit" )
      
        while True:
            # Get weather data
            data = get_weather_data(URL)

            # Build the message with simulated telemetry values.
            temperature = int(data['temperature'])
            precipitation = int(data['precipitation'].strip('%'))
            humidity = int(data['humidity'].strip('%'))
            wind = int(data['wind'].strip(' km/h'))
            msg_txt_formatted = MSG_TXT.format(temperature=temperature, precipitation=precipitation, humidity=humidity, wind=wind)
            message = Message(msg_txt_formatted)
            # Add a custom application property to the message.
            # An IoT hub can filter on these properties without access to the message body.
            if int(temperature) > 35: # High temperature warning
              message.custom_properties["temperatureAlert"] = "true"
            else:
              message.custom_properties["temperatureAlert"] = "false"

            # Send the message.
            print( "Sending message: {}".format(message) )
            client.send_message(message)
            print ( "Message successfully sent" )
            time.sleep(900)

    except KeyboardInterrupt:
        print ( "IoTHubClient sample stopped" )

if __name__ == '__main__':
    print ( "IoT Hub Quickstart #1 - Simulated device" )
    print ( "Press Ctrl-C to exit" )
    send_weather_data()