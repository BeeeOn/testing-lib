#!/bin/python3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import globalConfig

import logging
import MosquittoModule
import os
import random

import emulators.vektiva.smarwiEmulator as smarwiEmulator

class VektivaModule(MosquittoModule.MosquittoModule):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.vektivaConfig = {}
		self.vektivaConfig['smarwi'] = False

	def setUp(self):
		MQTT_BROKER_URL = "localhost"
		MAX_MAC = 2**48 - 1
		RANDOM_MAC = random.randint(1, MAX_MAC)
		DEFAULT_IP = "127.0.0.1"
		HTTP_SERVER_PORT = 6688

		self.GR.overrideUpdate("vektiva.enable", "yes")
		self.GR.overrideUpdate("vektiva.mqtt.host", MQTT_BROKER_URL)
		self.GR.overrideUpdate("vektiva.mqtt.port", str(globalConfig.mosquittoPort))
		super().setUp()

		if self.vektivaConfig['smarwi']:
			self.router = smarwiEmulator.Router(MQTT_BROKER_URL, globalConfig.mosquittoPort)
			self.router.devices("POST", '{"macAddr": "' + format(RANDOM_MAC, '012x') + '"}', "")
			self.server = smarwiEmulator.http_server(HTTP_SERVER_PORT, self.router)
			self.server.start()

	def tearDown(self):
		super().tearDown()

		if self.vektivaConfig['smarwi']:
			self.server.stop()
			self.server.join()

