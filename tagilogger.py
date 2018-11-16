#!/usr/bin/python3

import time
from ruuvitag_sensor.ble_communication import BleCommunicationNix
from ruuvitag_sensor.ruuvi import RuuviTagSensor
from ruuvitag_sensor.decoder import UrlDecoder
from ruuvitag_sensor.decoder import Df3Decoder
import config
import socket
import sys
import json

ble = BleCommunicationNix()

# list all your tags MAC: TAG_NAME
tags = config.tags;

# set DataFormat
# 1 - Weather station
# 3 - SensorTag data format 3 (under development)
dataFormat = '3'

import mysql.connector

conn = mysql.connector.connect(
         user='pi',
         password='<password>',
         host='<host>',
         port='3306',
         database='sensorData')

db = True # Enable or disable database saving True/False

if db:

    cur = conn.cursor()

    query = ("CREATE TABLE IF NOT EXISTS sensors (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, mac TEXT NOT NULL, name TEXT NOT NULL, temperature NUMERIC NULL, humidity NUMERIC NULL, pressure NUMERIC NULL);")

    cur.execute(query)

    conn.commit()
             
    cur.close()

# Extended RuuviTagSensor with name, and raw data output
class Rtag(RuuviTagSensor):

	def __init__(self, mac, name):
		self._mac = mac
		self._name = name

	@property
	def name(self):
		return self._name

	def getData(self):
		return ble.get_data(self._mac)

	
now = time.strftime('%Y-%m-%d %H:%M:%S')
print(now+"\n")

dbData = {}
	
for mac, name in tags.items():
	tag = Rtag(mac, name)

	print("Looking for {} ({})".format(tag._name, tag._mac))
	# if weather station
	if dataFormat == '3': # get parsed data

		dataTuple = RuuviTagSensor.convert_data(tag.getData())
		data = Df3Decoder().decode_data(dataTuple[1])
		print ("Data received:", data)
		daten = {}
		daten["name"] = tag._name
		daten["data"] = data

		daten1 = json.dumps(daten, ensure_ascii=False)

		dbData[tag._mac] = {'name': tag._name}
		# add each sensor with value to the lists
		for sensor, value in data.items():
			dbData[tag._mac].update({sensor: value})

	elif dataFormat == '3': # under development
		print ("Data:", tag.getData())
		
	else: # if unknown format, just print raw data
		print ("Data:", tag.getData())

	print("\n")

curs = conn.cursor()

if db:
	# save data to db
	for mac, content in dbData.items():
		curs.execute("INSERT INTO sensors (timestamp,mac,name,temperature,humidity,pressure) \
			VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".\
			format(now, mac, content['name'], content['temperature'], content['humidity'], content['pressure']))
	conn.commit()
	conn.close()
	print("Done.")
