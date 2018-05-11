#!/bin/python3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import globalConfig
import ApplicationRunner
import unittest
import logging
import os

class GatewayBaseModule(unittest.TestCase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.tmpDir = globalConfig.baseDir + "/tmp"
		if not os.path.exists(self.tmpDir):
			os.makedirs(self.tmpDir)
		outFile = self.tmpDir + "/gw" + self.__class__.__name__ + "." + self._testMethodName + ".out"
		errFile = self.tmpDir + "/gw" + self.__class__.__name__ + "." + self._testMethodName + ".out"
		self.GR = ApplicationRunner.ApplicationRunner(globalConfig.gatewayBinary, globalConfig.gatewayStartup, errFile, outFile)

	def setUp(self):
		logging.debug("basetest setUp")
		self.GR.start()

	def tearDown(self):
		logging.debug("basetest tearDown")
		res = self.GR.stop()
		logging.debug("Application exitted with return code %s" % res)
