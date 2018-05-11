#!/bin/python3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import globalConfig

import unittest
import logging
import MosquittoModule
import os
import random

import emulators.sonoffscEmulator as sonoffscEmulator

class SonoffModule(MosquittoModule.MosquittoModule):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.sonoffConfig = {}
		self.sonoffConfig['sc'] = False

	def setUp(self):
		MQTT_BROKER_URL = "localhost"
		MAX_MAC = 2**48 - 1
		RANDOM_MAC = random.randint(1, MAX_MAC)
		DEFAULT_IP = "127.0.0.1"

		self.GR.overrideUpdate("sonoff.enable", "yes")
		self.GR.overrideUpdate("sonoff.mqtt.host", MQTT_BROKER_URL)
		self.GR.overrideUpdate("sonoff.mqtt.port", str(globalConfig.mosquittoPort))
		super().setUp()

		if self.sonoffConfig['sc']:
			self.sonoffsc = sonoffscEmulator.VirtualSonoffSC(MQTT_BROKER_URL, globalConfig.mosquittoPort, DEFAULT_IP, RANDOM_MAC)
			self.sonoffsc.start()

	def tearDown(self):
		super().tearDown()
		if self.sonoffConfig['sc']:
			self.sonoffsc.stop()
			self.sonoffsc.join()
