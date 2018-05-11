#!/bin/python3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import globalConfig

import unittest
import time
import logging
import FakeGWServer
import GatewayBaseModule

defaultConfig = {'autoRegister' : False, 'autoData' : False, 'prePaired' : None, "autoResponse" : False, "autoNewDevice" : False}

class GWServerModule(GatewayBaseModule.GatewayBaseModule):
	def __init__(self, *args, **kwargs):
		self.gwsConfig = defaultConfig
		super().__init__(*args, **kwargs)

	def setUp(self):
		self.GR.overrideUpdate("gws.enable", "yes")
		self.GR.overrideUpdate("gws.host", "localhost")
		self.GR.overrideUpdate("gws.receiveTimeout", "10 s")
		self.GR.overrideUpdate("gws.port", str(globalConfig.gwsPort))
		self.GWS = FakeGWServer.FakeGWServer(globalConfig.gwsPort, self.gwsConfig)
		logging.debug("GWServerTest setUp")
		super().setUp()

	def tearDown(self):
		logging.debug("GWServerTest tearDown")
		self.GWS.stop()
		self.GWS.join()
		self.GWS = None
		super().tearDown()
