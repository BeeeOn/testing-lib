#!/bin/python3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import globalConfig

import GatewayBaseModule
import unittest
import NamedPipe
import logging

class NamedPipeModule(GatewayBaseModule.GatewayBaseModule):
	def setUp(self):
		logging.debug("NamedPipeTest setUp")
		pipePath = globalConfig.baseDir + "/beeeon_pipe"
		self.GR.overrideUpdate("exporter.pipe.enable", "yes")
		self.GR.overrideUpdate("exporter.pipe.path", pipePath)
		self.NP = NamedPipe.NamedPipe(pipePath)
		self.NP.start()
		super().setUp()

	def tearDown(self):
		logging.debug("NamedPipeTest tearDown")
		self.NP.stop()
		super().tearDown()
