#!/bin/python3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import globalConfig

import ServerBaseModule
import Gateway

class GatewayModule(ServerBaseModule.ServerBaseModule):
	def __init__(self, *args, **kwargs):
		self.gwAutoRegister = True
		super().__init__(*args, **kwargs)

	def setUp(self):
		self.SR.overrideUpdate("gws.ws.port", str(globalConfig.gwsPort))
		self.virtualGW = Gateway.Gateway(globalConfig.gwsPort, globalConfig.gwId, self.gwAutoRegister)
		super().setUp()

	def tearDown(self):
		self.virtualGW.close()
		super().tearDown()
