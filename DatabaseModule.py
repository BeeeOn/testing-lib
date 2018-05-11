#!/bin/python3

from testing import postgresql
import ServerBaseModule
import logging
import time

class DatabaseModule(ServerBaseModule.ServerBaseModule):
	def setUp(self):
		logging.debug("Database SetUp")
		self.pgInstance = postgresql.Postgresql()
		dsn = self.pgInstance.dsn()
		self.SR.overrideUpdate("database.host", str(dsn["host"]))
		self.SR.overrideUpdate("database.port", str(dsn["port"]))
		self.SR.overrideUpdate("database.user", str(dsn["user"]))
		self.SR.overrideUpdate("database.name", str(dsn["database"]))
		super().setUp()

	def tearDown(self):
		logging.debug("Database TearDown")
		time.sleep(5)
		self.pgInstance.terminate()
		super().tearDown()
