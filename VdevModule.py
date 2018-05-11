#!/bin/python3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import globalConfig

import unittest
import GatewayBaseModule
import logging

class VdevModule(GatewayBaseModule.GatewayBaseModule):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.vdevConfig = ""

	def setUp(self):
		configPath = globalConfig.baseDir + "/vdev.ini"
		self.GR.overrideUpdate("vdev.enable", "yes")
		self.GR.overrideUpdate("vdev.ini", configPath)
		with open(configPath, "w") as configFile:
			configFile.write(self.vdevConfig)

		logging.debug("VDEV setUp")
		super().setUp()

	def tearDown(self):
		logging.debug("VDEV tearDown")
		super().tearDown()
