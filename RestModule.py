#!/bin/python3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import globalConfig

from testing import postgresql
import ServerBaseModule
import logging
import time
import json
from rest import GET, POST, PUT, DELETE

class RestModule(ServerBaseModule.ServerBaseModule):
	def setUp(self):
		super().setUp()
		try:
			req = POST("localhost", globalConfig.uiPort, "/auth")
			req.body(globalConfig.PERMIT_LOGIN)
			response, content = req()

			self.assertEqual(200, response.status)
			result = json.loads(content)

			self.assertEqual("success", result["status"])

			self.session = result["data"]["id"]
		except Exception as ex:
			self.tearDown()
			raise ex

	def tearDown(self):
		try:
			req = DELETE("localhost", globalConfig.uiPort, "/auth")
			req.authorize(self.session)
			response, content = req()

			self.assertEqual(204, response.status)
		finally:
			super().tearDown()

	def assignGateway(self, gwId, name):
		req = POST("localhost", globalConfig.uiPort, "/gateways")
		req.authorize(self.session)
		req.body(json.dumps({
			"id": gwId,
			"name": name,
			"timezone_id": "Europe/Prague"
		}))

		response, content = req()
		self.assertEqual(201, response.status)
		self.assertEqual("/gateways/" + gwId,
				response.getheader("Location"))

		# check the gateway's contents
		resultLink = response.getheader("Location")
		req = GET("localhost", globalConfig.uiPort, resultLink)
		req.authorize(self.session)

		response, content = req()
		self.assertEqual(200, response.status)

		result = json.loads(content)
		self.assertEqual("success", result["status"])
		self.assertEqual("My Home", result["data"]["name"])
		self.assertEqual(gwId, result["data"]["id"])
		self.assertEqual("Europe/Prague", result["data"]["timezone"]["id"])
		return resultLink

	def unassignGateway(self, gwId, resultLink):
		# unassign the gateway
		req = DELETE("localhost", globalConfig.uiPort, "/gateways/" + gwId)
		req.authorize(self.session)
		response, content = req()

		self.assertEqual(204, response.status)

		# test the gateway is inaccessible
		req = GET("localhost", globalConfig.uiPort, resultLink)
		req.authorize(self.session)

		response, content = req()
		self.assertEqual(403, response.status)
		result = json.loads(content)
		self.assertEqual(403, result["code"])
		self.assertEqual("not enough permission to access the resource", result["message"])

	def deviceDiscovery(self, gwId, timeLimit = "10"):
		req = POST("localhost", globalConfig.uiPort, "/gateways/" + str(gwId) + "/discovery")
		req.authorize(self.session)
		req.body(json.dumps({
			"time_limit": timeLimit,
		}))

		response, content = req()
		self.assertEqual(202, response.status)

	def getDevices(self, gwId):
		req = GET("localhost", globalConfig.uiPort, "/gateways/" + str(gwId) + "/devices")
		req.authorize(self.session)

		response, content = req()
		self.assertEqual(200, response.status)
		return json.loads(content)['data']

	def activateDevice(self, gwId, deviceId, name):
		req = PUT("localhost", globalConfig.uiPort, "/gateways/" + str(gwId) + "/devices/" + str(deviceId))
		req.authorize(self.session)
		req.body(json.dumps({
			"name": name,
		}))

		response, content = req()
		self.assertEqual(200, response.status)

	def unpairDevice(self, gwId, deviceId):
		req = DELETE("localhost", globalConfig.uiPort, "/gateways/" + str(gwId) + "/devices/" + str(deviceId))
		req.authorize(self.session)

		response, content = req()
		self.assertEqual(202, response.status)

	def currentDeviceValue(self, gwId, deviceId, moduleId):
		req = GET("localhost", globalConfig.uiPort, "/gateways/" + str(gwId) + "/devices/" + str(deviceId) + "/sensors/"+str(moduleId)+"/current")
		req.authorize(self.session)

		response, content = req()
		self.assertEqual(200, response.status)
		return json.loads(content)['data']

	def requestChange(self, gwId, deviceId, moduleId, value):
		req = POST("localhost", globalConfig.uiPort, "/gateways/" + str(gwId) + "/devices/" + str(deviceId) + "/controls/"+str(moduleId)+"/current")
		req.authorize(self.session)
		req.body(json.dumps({
			"value": value,
		}))

		response, content = req()
		self.assertEqual(200, response.status)
		print("CONTENT: " + str(content))
