#!/bin/python3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import globalConfig

import unittest
import GatewayBaseModule
import logging
import random

import emulators.phuemuBridge as phuemuBridge

class PhilipsModule(GatewayBaseModule.GatewayBaseModule):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.phuemuConfig = {}
		self.phuemuConfig['bulb'] = False

	def setUp(self):
		DEFAULT_IP = '127.0.0.1'
		MAX_MAC = 2**48 - 1
		RANDOM_MAC_BRIDGE = random.randint(1,MAX_MAC)
		RANDOM_PORT_BRIDGE = random.randint(49152, 65535)

		self.GR.overrideUpdate("philipshue.enable", "yes")
		self.GR.overrideUpdate("philipshue.refresh", "3 s")
		self.GR.overrideUpdate("philipshue.upnp.timeout", "2 s")
		if self.phuemuConfig['bulb']:
			self.phuemuBridge = phuemuBridge.VirtualPhilipsHueBridge(DEFAULT_IP, RANDOM_PORT_BRIDGE, RANDOM_MAC_BRIDGE, 1)
			self.phuemuBridge.start()
		super().setUp()

	def tearDown(self):
		if self.phuemuConfig['bulb']:
			self.phuemuBridge.stop()
			self.phuemuBridge.join()
		super().tearDown()
