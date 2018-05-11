#!/bin/python3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import globalConfig

import GatewayBaseModule
import MosquittoRunner
import logging
import os

class MosquittoModule(GatewayBaseModule.GatewayBaseModule):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.tmpDir = globalConfig.baseDir + "/tmp"
		if not os.path.exists(self.tmpDir):
			os.makedirs(self.tmpDir)
		outFile = self.tmpDir + "/gw" + self.__class__.__name__ + ".Mosquitto." + self._testMethodName + ".out"
		errFile = self.tmpDir + "/gw" + self.__class__.__name__ + ".Mosquitto." + self._testMethodName + ".out"
		self.MR = MosquittoRunner.MosquittoRunner(globalConfig.mosquittoBinary, globalConfig.mosquittoPort, errFile, outFile)

	def setUp(self):
		logging.debug("mosquitto setUp")
		self.MR.start()
		super().setUp()

	def tearDown(self):
		super().tearDown()
		logging.debug("mosquitto tearDown")
		res = self.MR.stop()
		logging.debug("mosquitto exitted with return code %s" % res)
