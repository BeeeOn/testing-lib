#!/bin/python3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import globalConfig

import unittest
import GatewayBaseModule
import logging
import random

import emulators.bewemuSwitch as bewemuSwitch
import emulators.bewemuDimmer as bewemuDimmer
import emulators.bewemuLink as bewemuLink

class BelkinModule(GatewayBaseModule.GatewayBaseModule):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.bewemuConfig = {}
		self.bewemuConfig['switch'] = False
		self.bewemuConfig['dimmer'] = False
		self.bewemuConfig['link'] = False

	def setUp(self):
		DEFAULT_IP = '127.0.0.1'
		DEFAULT_SERIAL_NUMBER = "221618K1100220"
		MAX_MAC = 2**48 - 1
		RANDOM_MAC_SWITCH = random.randint(1,MAX_MAC)
		RANDOM_PORT_SWITCH = random.randint(49152, 65535)
		RANDOM_MAC_DIMMER = random.randint(1,MAX_MAC)
		RANDOM_PORT_DIMMER = random.randint(49152, 65535)
		RANDOM_MAC_LINK = random.randint(1,MAX_MAC)
		RANDOM_PORT_LINK = random.randint(49152, 65535)

		self.GR.overrideUpdate("belkinwemo.enable", "yes")
		self.GR.overrideUpdate("belkinwemo.refresh", "3 s")
		self.GR.overrideUpdate("belkinwemo.upnp.timeout", "2 s")
		if self.bewemuConfig['switch']:
			self.bewemuSwitch = bewemuSwitch.VirtualBelkinWemoSwitch(DEFAULT_IP, RANDOM_PORT_SWITCH, RANDOM_MAC_SWITCH, DEFAULT_SERIAL_NUMBER)
			self.bewemuSwitch.start()
		if self.bewemuConfig['dimmer']:
			self.bewemuDimmer = bewemuDimmer.VirtualBelkinWemoDimmer(DEFAULT_IP, RANDOM_PORT_SWITCH, RANDOM_MAC_SWITCH, DEFAULT_SERIAL_NUMBER)
			self.bewemuDimmer.start()
		if self.bewemuConfig['link']:
			self.bewemuLink = bewemuLink.VirtualBelkinWemoLink(DEFAULT_IP, RANDOM_PORT_SWITCH, RANDOM_MAC_SWITCH, DEFAULT_SERIAL_NUMBER, 1)
			self.bewemuLink.start()
		super().setUp()

	def tearDown(self):
		if self.bewemuConfig['switch']:
			self.bewemuSwitch.stop()
			self.bewemuSwitch.join()
		if self.bewemuConfig['dimmer']:
			self.bewemuDimmer.stop()
			self.bewemuDimmer.join()
		if self.bewemuConfig['link']:
			self.bewemuLink.stop()
			self.bewemuLink.join()
		super().tearDown()
