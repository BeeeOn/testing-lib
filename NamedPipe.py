#!/bin/python3

import sys
import threading
import os
import select
import time

"""
Class for reading data in background thread
from specified named pipe.
"""
class NamedPipe (threading.Thread):
	def __init__(self, filePath):
		threading.Thread.__init__(self)
		self.filePath = filePath
		self.exit = False
		self.data = []
		self.lock = threading.Lock()
		self.event = threading.Event()
		self.leftover = ""
		self.clearData()

	def run(self):
		pipe = None
		selectTimeout = 0.25
		while not self.exit:
			try:
				if (pipe == None):
					pipe = os.open(self.filePath, os.O_RDONLY|os.O_NONBLOCK)
				(r,w,e) = select.select([pipe],[],[], selectTimeout)
				if not r:
					continue

				data = os.read(pipe, 4096).decode('utf-8')
				if len(data) == 0:
					os.close(pipe)
					pipe = None
					continue

				data = self.leftover + data
				self.leftover = ""
				lines = data.split('\n')
				if data[-1] != '\n':
					self.leftover = lines[-1]
					lines = lines[:-1]
			except:
				time.sleep(1)
				continue

			with self.lock:
				self.lines = self.lines + lines
				self.lines = [x for x in self.lines if x != ""]
				self.event.set()

	def wait(self, timeout = None):
		return self.event.wait(timeout)

	def nextData(self):
		result = None
		with self.lock:
			if self.lines:
				result = self.lines.pop(0)
			if not self.lines:
				self.event.clear()
			return result

	def clearData(self):
		with self.lock:
			self.lines = []
			self.event.clear()

	def stop(self):
		self.exit = True
