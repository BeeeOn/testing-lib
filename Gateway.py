import websocket
import json
import SensorData

def assureNotClosed(self, ws, timeout = 1):
	ws.socket.timeout = timeout
	with self.assertRaises(websocket.WebSocketTimeoutException):
		ws.recv()

def assureIsClosed(self, ws):
	with self.assertRaises(websocket.WebSocketConnectionClosedException):
		ws.recv()
"""
This class is responsible for emulation of real BeeeOn Gateway.
It is able to connect to GW Server and manage some of the
control messages.
"""
class Gateway:
	def __init__(self, port, id,  autoRegister, host = "localhost"):
		self.socket = None
		self.port = port
		self.host = host
		self.id = id
		self.autoRegister = autoRegister

	def connect(self):
		self.socket = websocket.WebSocket()
		self.socket.connect("ws://%s:%u" %(self.host, self.port))
		if self.autoRegister:
			msg = {}
			msg['gateway_id'] = self.id
			msg['message_type'] = "gateway_register"
			msg['version'] = "v1.0"
			msg['ip_address'] = "192.168.1.1"
			self.socket.send(json.dumps(msg))
			answer = json.loads(self.socket.recv())
			if answer['message_type'] != "gateway_accepted":
				raise Exception("error registering")

	def send(self, msg):
		self.socket.send(msg)

	def recv(self):
		return self.socket.recv()

	def close(self):
		try:
			self.socket.close()
		except:
			pass

	def socket(self):
		return self.socket
