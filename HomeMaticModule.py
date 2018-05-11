#!/bin/python3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import globalConfig

import unittest
import GatewayBaseModule
import logging
import random

import emulators.fhemEmulator as fhemEmulator

class HomeMaticModule(GatewayBaseModule.GatewayBaseModule):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fhemuConfig = {}
		self.fhemuConfig['switch'] = False
		self.fhemuConfig['contact'] = False

	def setUp(self):
		DEFAULT_IP = '127.0.0.1'
		DEFAULT_SERIAL_NUMBER = "MEQ0106579"
		MAX_MAC = 2**48 - 1
		RANDOM_MAC_DEVICE = random.randint(1,MAX_MAC)
		DEFAULT_PORT = 7076

		self.GR.overrideUpdate("conrad.enable", "yes")
		self.GR.overrideUpdate("conrad.fhem.address", DEFAULT_IP + ":" + str(DEFAULT_PORT))
		self.GR.overrideUpdate("conrad.fhem.refreshTime", "3 s")
		if self.fhemuConfig['switch']:
			self.fhemu = fhemEmulator.VirtualFHEMServer(DEFAULT_IP, DEFAULT_PORT, 'switch', RANDOM_MAC_DEVICE, DEFAULT_SERIAL_NUMBER)
			self.fhemu.start()
		if self.fhemuConfig['contact']:
			self.fhemu = fhemEmulator.VirtualFHEMServer(DEFAULT_IP, DEFAULT_PORT, 'contact', RANDOM_MAC_DEVICE, DEFAULT_SERIAL_NUMBER)
			self.fhemu.start()
		super().setUp()

	def tearDown(self):
		if self.fhemuConfig['switch'] or self.fhemuConfig['contact']:
			self.fhemu.stop()
			self.fhemu.join()
		super().tearDown()
