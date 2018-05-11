#!/bin/python3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import globalConfig
import ApplicationRunner
import unittest
import logging

import os

class ServerBaseModule(unittest.TestCase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.tmpDir = globalConfig.baseDir + "/tmp"
		if not os.path.exists(self.tmpDir):
			os.makedirs(self.tmpDir)
		outFile = self.tmpDir + "/server." + self.__class__.__name__ + "." + self._testMethodName + ".out"
		errFile = self.tmpDir + "/server." + self.__class__.__name__ + "." + self._testMethodName + ".out"
		self.SR = ApplicationRunner.ApplicationRunner(globalConfig.serverBinary, globalConfig.serverStartup, errFile, outFile)

	def setUp(self):
		logging.debug("server basetest setUp")
		self.SR.start()
		super().setUp()

	def tearDown(self):
		logging.debug("server basetest tearDown")
		res = self.SR.stop()
		logging.debug("Application exitted with return code %s" % res)
		super().tearDown()
