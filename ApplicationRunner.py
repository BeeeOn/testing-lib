#!/bin/python3

import os
import signal
import sys
import threading

import logging

from threading import Timer

"""
This class is responsible for running BeeeOn application
in forked process in the background. stderr and stdout
are redirected to specified files.

Every BeeeOn application is supposed to send SIGTERM signal to
specified process on successfull initialization(via the "-N{PID} argument").
This signal is expected to be received in a specified timeout.

This object is thread unsafe and should be handled within a single thread.
"""
class ApplicationRunner:
	"""
	Creates an application runner.

	Arguments:
	binaryPath -- application's executable path.
	configPath -- main configuration file used for application, its used as "-c argument".
	stderrFile -- Application's stderr is redirected to this file.
	stdoutFile -- Application's stdout is redirected to this file.
	startupTimeout -- Timeout for application to start, if the SIGTERM is not received in this timeout, application is killed.
	"""
	def __init__(self, binaryPath, configPath, stderrFile, stdoutFile, valgrind = False, startupTimeout = 5):
		self.binaryPath = binaryPath
		self.configPath = configPath
		self.valgrind = valgrind
		self.override = {}
		self.pid = None
		self.stderrFile = stderrFile
		self.stdoutFile = stdoutFile
		self.startupTimeout = startupTimeout
		self.event = threading.Event()

	def overrideUpdate(self, key, value):
		self.override[key] = value

	def startupHandler(self, signum, frame):
		self.event.set()

	def start(self):
		if self.pid != None:
			raise Exception("Already running")

		signal.signal(signal.SIGTERM, self.startupHandler)
		parentPid = os.getpid()

		logging.debug("Override options: " + str(self.override))
		pid = os.fork()
		if (pid == 0): # child
			fdout = os.open(self.stdoutFile, os.O_WRONLY|os.O_CREAT|os.O_TRUNC)
			fderr = os.open(self.stderrFile, os.O_WRONLY|os.O_CREAT|os.O_TRUNC)
			os.dup2(fdout, sys.stdout.fileno())
			os.dup2(fderr, sys.stderr.fileno())
			if self.valgrind:
				args = ["/usr/bin/valgrind", self.binaryPath, "-c", self.configPath]
			else:
				args = [self.binaryPath, "-c", self.configPath]
			for key, value in self.override.items():
				args.append("-D" + key + "=" + value)
			args.append("-N" + str(parentPid))
			if self.valgrind:
				os.execv("/usr/bin/valgrind", args)
			else:
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
