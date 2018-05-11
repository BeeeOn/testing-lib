import time
import Device
import logging
import SensorData
import threading
import json
import uuid
from websocket_server import WebsocketServer
import websocket_server


"""
This class is responsible for real GW Server emulation
"""
class FakeGWServer(threading.Thread):
	"""
	Creates an FakeGWServer.

	Arguments:
	port -- port of WebSocket connection.
	config -- configuration of behaviour, could contain following parameters:
		'autoRegister' -- automatic registration accepting
		'autoResponse' -- automatic response for requests
		'autoData' -- automatic data messages processing
		'prePaired' -- list of paired devices for device_list requests.
		'autoNewDevice' -- automatic new device reqests handling
	"""
	def __init__(self, port, config, host = '127.0.0.1'):
		self.autoRegister = config['autoRegister']
		self.autoResponse = config['autoResponse']
		self.autoData = config['autoData']
		self.prePaired = config['prePaired']
		self.autoNewDevice = config['autoNewDevice']

		self.WSServer = WebsocketServer(port, host, loglevel=logging.DEBUG)
		self.WSServer.set_fn_message_received(self.message_received)
		self.WSServer.set_fn_client_left(self.client_left)
		self.WSServer.set_fn_new_client(self.new_client)

		self.messages = []
		self.dataMessages = []
		self.responseMessages = []
		self.newDevices = []
		self.client = None
		self.clientLock = threading.Lock()
		self.newConnection = threading.Condition(self.clientLock)
		self.disconnect = threading.Condition(self.clientLock)
		self.newMessage = threading.Condition(self.clientLock)
		self.newDataMessage = threading.Condition(self.clientLock)
		self.newResponseMessage = threading.Condition(self.clientLock)
		self.newDeviceMessage = threading.Condition(self.clientLock)
		self.connected = False
		self.resetEnable = False
		super().__init__()

	def run(self):
		self.WSServer.run_forever()
		self.WSServer.socket.close()

	def stop(self):
		self.WSServer.shutdown()

	def enableReset(self):
		with self.clientLock:
			self.resetEnable = True

	def new_client(self, client, server):
		with self.clientLock:
			if self.connected:
				logging.debug("Unknown client refused")
				client['handler'].send_text("", websocket_server.OPCODE_CLOSE_CONN)
			elif self.client is None or self.resetEnable:
				self.client = client
				if not self.autoRegister:
					self.connected = True
					self.newConnection.notify_all()
				self.resetEnable = False
				logging.debug("connection established")
			else:
				logging.debug("dropping completely")
				client['handler'].send_text("", websocket_server.OPCODE_CLOSE_CONN)

	def client_left(self, client, server):
		with self.clientLock:
			if client == self.client:
				logging.debug("client disconnected")
				self.connected = False
				self.messages = []
				self.disconnect.notify_all()
			else:
				logging.debug("unknown client disconnected")

	def message_received(self, client, server, message):
		logging.debug("received: " + message)
		with self.clientLock:
			if self.client != client:
				logging.debug("dropping message from unknown client")
				return
			try:
				jsonMessage = json.loads(message)
				if self.autoRegister:
					if jsonMessage['message_type'] == "gateway_register":
						self.WSServer.send_message(self.client, '{ "message_type" : "gateway_accepted" }')
						self.connected = True
						self.newConnection.notify_all()
						return
				if self.autoData:
					if jsonMessage['message_type'] == "sensor_data_export":
						sensorData = SensorData.SensorData()
						sensorData.fromJSON(jsonMessage['data'][0])
						self.dataMessages.append(sensorData)
						self.newDataMessage.notify_all()
						response = {}
						response['message_type'] = "sensor_data_confirm"
						response['id'] = jsonMessage['id']
						logging.debug("sending message: " + json.dumps(response))
						self.WSServer.send_message(self.client, json.dumps(response))
						return
				if self.prePaired is not None:
					if jsonMessage['message_type'] == "device_list_request":
						if jsonMessage['device_prefix'] in self.prePaired:
							response = {}
							response['message_type'] = "device_list_response"
							response['id'] = jsonMessage['id']
							response['status'] = 1
							response['devices'] = self.prePaired[jsonMessage['device_prefix']]
							logging.debug("sending message: " + json.dumps(response))
							self.WSServer.send_message(self.client, json.dumps(response))
						return
				if self.autoResponse:
					if jsonMessage['message_type'] == "response_with_ack":
						self.responseMessages.append(jsonMessage)
						self.newResponseMessage.notify_all()
						response = {}
						response['message_type'] = "generic_ack"
						response['id'] = jsonMessage['id']
						response['status'] = jsonMessage['status']
						logging.debug("sending message: " + json.dumps(response))
						self.WSServer.send_message(self.client, json.dumps(response))
						return
					if jsonMessage['message_type'] == "generic_response":
						self.responseMessages.append(jsonMessage)
						self.newResponseMessage.notify_all()
						return

				if self.autoNewDevice:
					if jsonMessage['message_type'] == "new_device_request":
						device = Device.Device(jsonMessage)
						self.newDevices.append(device)
						self.newDeviceMessage.notify_all()
						response = {}
						response['message_type'] = "generic_ack"
						response['id'] = jsonMessage['id']
						response['status'] = 1
						logging.debug("sending message: " + json.dumps(response))
						self.WSServer.send_message(self.client, json.dumps(response))
						return

			except Exception as ex:
				logging.error("Exception: " + str(ex))
				pass

			self.messages.append(message)
			self.newMessage.notify_all()

	def nextNewDevice(self, timeout = 10):
		with self.clientLock:
			if not self.newDevices:
				self.newDeviceMessage.wait(timeout)
			if self.newDevices:
				return self.newDevices.pop(0)

	def nextResponse(self, timeout = 10):
		with self.clientLock:
			if not self.responseMessages:
				self.newResponseMessage.wait(timeout)
			if self.responseMessages:
				return self.responseMessages.pop(0)

	def nextData(self, timeout = 10):
		with self.clientLock:
			if not self.dataMessages:
				self.newDataMessage.wait(timeout)
			if self.dataMessages:
				return self.dataMessages.pop(0)

	def clearData(self):
		with self.clientLock:
			self.dataMessages = []

	def nextMessage(self, timeout = 10):
		with self.clientLock:
			if not self.messages:
				self.newMessage.wait(timeout)
			if self.messages:
				return self.messages.pop(0)

	def waitForDisconnect(self, timeout = 10):
		with self.clientLock:
			if not self.connected:
				return True
			self.disconnect.wait(timeout)
			return not self.connected

	def waitForConnection(self, timeout = 10):
		with self.clientLock:
			if self.connected:
				return True
			self.newConnection.wait(timeout)
			return self.connected

	def sendMessage(self, message):
		with self.clientLock:
			if self.connected:
				logging.debug("sending message: " + message)
				self.WSServer.send_message(self.client, message)
			else:
				raise Exception("client is not connected")

class Commander:
	def __init__(self, gwServer):
		self.gwServer = gwServer

	def listen(self, timeout = 10, duration = "10"):
		command = self.createBaseCommand("listen_request")
		command['duration'] = duration
		self.gwServer.sendMessage(json.dumps(command))
		return self.waitUntilFinished(command['id'], timeout)

	def deviceAccept(self, deviceID, timeout = 10):
		command = self.createBaseCommand("device_accept_request")
		command['device_id'] = deviceID
		self.gwServer.sendMessage(json.dumps(command))
		return self.waitUntilFinished(command['id'], timeout)

	def unpair(self, deviceID, timeout = 10):
		command = self.createBaseCommand("unpair_request")
		command['device_id'] = deviceID
		self.gwServer.sendMessage(json.dumps(command))
		return self.waitUntilFinished(command['id'], timeout)

	def deviceSetValue(self, deviceID, moduleID, value, commandTimeout = "10", timeout = 10):
		command = self.createBaseCommand("set_value_request")
		command['device_id'] = deviceID
		command['module_id'] = moduleID
		command['value'] = value
		command['timeout'] = commandTimeout
		self.gwServer.sendMessage(json.dumps(command))
		return self.waitUntilFinished(command['id'], timeout)

	def waitUntilFinished(self, id, timeout):
		while True:
			response = self.gwServer.nextResponse(timeout)
			if response is None:
				raise Exception("Command did not finish in timeout")
			if id != response['id']:
				continue
			status = int(response['status'])
			if status > 0:
				return status

	def createBaseCommand(self, message_type):
		command = {}
		command['message_type'] = message_type
		command['id'] = str(uuid.uuid1())
		return command
