class Module:
	def __init__(self, type, attributes):
		self.type = type
		self.attributes = attributes

class Device:
	def __init__(self, jsonMessage):
		self.fromJSON(jsonMessage)

	def fromJSON(self, jsonMessage):
		self.name = jsonMessage['product_name']
		self.vendor = jsonMessage['vendor']
		self.refresh = int(jsonMessage['refresh_time'])
		self.id = jsonMessage['device_id']
		self.moduleTypes = []
		for moduleType in jsonMessage['module_types']:
			attributes = []
			for attribute in moduleType['attributes']:
				attributes.append(attribute['attribute'])
			self.moduleTypes.append((moduleType['type'], attributes))
