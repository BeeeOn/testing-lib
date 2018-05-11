#!/bin/python3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import globalConfig

import unittest
import GatewayBaseModule
import logging

class PressureModule(GatewayBaseModule.GatewayBaseModule):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.vdevConfig = ""

	def setUp(self):
		configPath = globalConfig.baseDir + "/vdev.ini"
		self.pressureFile = globalConfig.baseDir + "/pressure_in"
		self.GR.overrideUpdate("psdev.enable", "yes")
		self.GR.overrideUpdate("psdev.path", self.pressureFile)
		self.GR.overrideUpdate("psdev.refresh", "2 s")
		with open(self.pressureFile, "w") as configFile:
			configFile.write("1234")
		super().setUp()
