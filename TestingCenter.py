#!/bin/python3

import socket

import time
import logging


"""
This class is responsible for connecting to BeeeOn gateway
running TestingCenter on specific host and port, with use
of class Commander, we are able to send commands to Gateway.
"""
class TestingCenter:

	PROMPT = "> "

	def __init__(self, host, port):
		self.sockAddr = (host, port)
		self.socket = None

	def connect(self):
		connectCount = 0
		connectLimit = 5
		while self.socket is None:
			try:
				self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.socket.connect(self.sockAddr)
				message = self.nextMessage()
			except Exception as ex:
				connectCount += 1
				if connectCount < connectLimit:
					print("connecting failed, retry")
					time.sleep(1)
				else:
					raise ex

	"""
	Send the given message to testing center. Newline character is automatically
	appended at the end of the message.
	"""
	def send(self, message):
		if self.socket is None:
			self.connect()
		message = message + "\n"
		self.socket.sendall(message.encode())
		logging.debug("Sending message:\"" + message + "\"")

	"""
	Receive data from TestingCenter until next console prompt
	is received. Return list of loaded lines from TestingCenter.
	"""
	def nextMessage(self): # TODO timeout
		acc = ""
		stop = False
		while not stop:
			data = self.socket.recv(4096)
			acc += data.decode('utf-8')
			logging.debug("Received: \"" + data.decode('utf-8') + "\"")
			if (TestingCenter.PROMPT) in acc:
				return acc.split("\n")[:-1]

	def listDevices(self):
		self.send("device list-new")
		return self.nextMessage()

	def disconnect(self):
		if not self.socket is None:
			self.socket.close()

	def createCommander(self):
		return Commander(self)

class Commander:
	def __init__(self, testingCenter):
		self.testingCenter = testingCenter

	def waitForDone(self, lastResponse, timeout):
		response = lastResponse

		while not self.isDone(response[0]):
			self.testingCenter.send("wait-queue " + timeout)
			response = self.testingCenter.nextMessage()
			if len(response) != 1:
				logging.critical("COMMAND DID NOT FINISHED")
				raise Exception("command did not finish in timeout")

		return response

	def sendCommand(self, command, timeout="15000"):
		self.testingCenter.send(command)
		response = self.testingCenter.nextMessage()
		if "error" in response[0]:
			return (0,0)
		response = self.waitForDone(response, timeout)

		return self.parseResult(response)

	def isDone(self, message):
		return "DONE" in message

	"""
	Parse the result for sent command or wait-queue expected in
	format "COMMANDID DONE X/X [{S,F}]"
	E.g.:
	"0x7F0188004600 DONE 6/6 SSSSSS"
	"0x7F0188004600 DONE 6/6 SSFSSF"
	"0x7F0188004600 DONE 0/0"

	Return tuple containing count of success and failures.
	"""
	def parseResult(self, result):
		tokens = result[0].split(" ")
		success = 0
		failure = 0

		if len(tokens) == 4:
			for resultChar in tokens[-1]:
				if resultChar == "S":
					success += 1
				elif resultChar == "F":
					failure += 1

		return (success, failure)


	def listen(self, timeout = ""):
		commandTimeout = (int(timeout) + 10) * 1000
		return self.sendCommand("command listen %s" % timeout, str(commandTimeout))

	def deviceAccept(self, deviceID):
		return self.sendCommand("command device-accept %s" % deviceID)

	def unpair(self, deviceID):
		return self.sendCommand("command unpair %s" % deviceID)

	def deviceSetValue(self, deviceID, moduleID, value, timeout = ""):
		return self.sendCommand("command set-value %s %s %s %s" % (deviceID, moduleID, value, timeout))

	"""
	Send echo message and receive echo response. Given message and its response should be identical strings. This
	comparison can be used to verify basic functionality of connected TestingCenter.
	"""
	def echo(self, message):
		self.testingCenter.send("echo " + message)
		return self.testingCenter.nextMessage()[0]
