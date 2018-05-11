#!/bin/python3

import csv
import json

"""
Python representation of BeeeOn sensor data,
which holds deviceID, timestamp and data list with touples
of (moduleID, value)
"""
class SensorData:
	def fromJSON(self, jsonData):
		self.timestamp = jsonData['timestamp']
		self.deviceID = jsonData['device_id']
		self.data = []
		for moduleData in jsonData['values']:
			module = int(moduleData['module_id'])
			value = float(moduleData['value'])
			self.data.append((module, value))

	def fromCSV(self, stringData, delimiter = ";"):
		reader = csv.reader([stringData], delimiter=delimiter)
		csvList = list(reader)
		csvList = list(filter(None, csvList[0])) # remove empty stringsa

		if len(csvList) < 5:
			raise Exception("parsing error: items count should be at least 5")
		if (len(csvList) % 2) != 1:
			raise Exception("parsing error: ")
		if csvList[0] != "sensor":
			raise Exception("parsing error: first item should be \"sensor\" string")

		self.timestamp = csvList[1]
		self.deviceID = csvList[2]

		csvList = csvList[3::]

		self.data = []
		while csvList:
			self.data.append((int(csvList[0]), float(csvList[1])))
			csvList = csvList[2::]

	def toCSV(self, delimiter = ";"):
		result = "sensor" + delimiter
		result += self.timestamp + delimiter + self.deviceID + delimiter
		for sensorValue in self.data:
			result += sensorValue[0] + delimiter + sensorValue[1] + delimiter
		return result
