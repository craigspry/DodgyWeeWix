import serial
import paho.mqtt.client as paho
import json
import time

def on_publish(client, userdata, result):
    print('Published Data {} result {}'.format(userdata, result))
    pass


client1 = paho.Client("weather_station")
#  client1.on_publish = on_publish
client1.connect('localhost', 1883)

try:
    ser = serial.Serial('/dev/ttyUSB0')
    while True:
        data = ser.readline()
        #  print(data)
        reading = data.decode('utf-8').replace('\n', '').replace('\r', '').split(',')
        #  print(reading)
        if len(reading) > 2:
            client1.publish('weather/temperature', reading[1])
            client1.publish('weather/humidity', reading[0])
            client1.publish('weather/pressure', reading[2])
            client1.publish('weather/dewpoint', reading[4])
            client1.publish('weather/cloudheight', reading[5])
            client1.publish('weather/winddir', reading[6])
            client1.publish('weather/windspeed', reading[7])
            client1.publish('weather/rainfall', reading[8])
            msgdict = {"temperature": reading[1],
                       "humidity": reading[0],
                       "pressure": reading[2],
                       "dewpoint": reading[4],
                       "cloudheight": reading[5],
                       "winddir": reading[6],
                       "windspeed": reading[7],
                       "rainfall": reading[8]}
            client1.publish('weather/all', json.dumps(msgdict))
except:
    while True:
        time.sleep(20)
