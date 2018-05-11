#!/bin/python3

import GatewayBaseModule
import unittest
import time
import TestingCenter
import logging

class TCModule(GatewayBaseModule.GatewayBaseModule):
	def setUp(self):
		TC_PORT = 6001
		self.GR.overrideUpdate("testing.center.enable", "yes")
		self.GR.overrideUpdate("testing.center.tcp.port", str(TC_PORT))
		self.TC = TestingCenter.TestingCenter("localhost", TC_PORT)
		logging.debug("TCTEST setUp")
		super().setUp()

	def tearDown(self):
		logging.debug("TCTEST tearDown")
		self.TC.disconnect()
		super().tearDown()
