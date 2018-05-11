#!/bin/python3

import os
import signal
import sys
import threading

import logging

from threading import Timer

class MosquittoRunner:
	def __init__(self, binaryPath, port, stderrFile, stdoutFile, startupTimeout = 5):
		self.binaryPath = binaryPath
		self.port = port
		self.pid = None
		self.stderrFile = stderrFile
		self.stdoutFile = stdoutFile
		self.startupTimeout = startupTimeout
		self.event = threading.Event()

	def startupHandler(self, signum, frame):
		self.event.set()

	def start(self):
		if self.pid != None:
			raise Exception("Already running")

		signal.signal(signal.SIGTERM, self.startupHandler)
		parentPid = os.getpid()

		pid = os.fork()
		if (pid == 0): # child
			fdout = os.open(self.stdoutFile, os.O_WRONLY|os.O_CREAT|os.O_TRUNC)
			fderr = os.open(self.stderrFile, os.O_WRONLY|os.O_CREAT|os.O_TRUNC)
			os.dup2(fdout, sys.stdout.fileno())
			os.dup2(fderr, sys.stderr.fileno())
			args = [self.binaryPath, "-p", str(self.port)]
			os.execv(self.binaryPath, args)
		else:
			self.pid = pid
			res = self.event.wait(self.startupTimeout)
			self.event.clear()
			return res

	def stop(self, timeout = 15):
		kill = lambda pid: (os.kill(pid, signal.SIGKILL))

		if self.pid is None:
			raise Exception("Nothing to stop")

		killTimer = Timer(timeout, kill, [self.pid])

		try:
			killTimer.start()
			os.kill(self.pid, signal.SIGINT)
			res = os.waitpid(self.pid, 0)
			return res[1]
		finally:
			killTimer.cancel()
			self.pid = None
