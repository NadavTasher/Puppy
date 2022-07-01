# Import python libraries
import socket

class Browser(object):
	# Initialize constants
	
	def __init__(self):
		# Socket variables
		self._socket, self._protocol = None, socket.AF_INET
		self._source, self._destination = None, None

		# HTTP variables
		self._linger = False
		self._compress = False

		# Browser variables
		self._cookies = dict()
		self._headers = list()
		self._history = list()

	@property
	def connected(self):
		# Check if the socket is set
		return self._socket is not None

	def wrap(self, *wrappers):
		# Make sure the socket exists
		assert self._socket, "Socket does not exist"

		# Wrap the socket with all wrappers
		for wrapper in wrappers:
			self._socket = wrapper(self._socket)

	def socket(self, source=None, destination=None, protocol=None, *wrappers):
		# Make sure socket does not exist
		assert not self._socket, "Socket already exists"

		# Decide which addresses to use
		source = source or self._source
		destination = destination or self._destination

		# Make sure addresses are valid
		assert source and destination, "Addresses are not valid"

		# Decide which protocol to use
		protocol = protocol or self._protocol

		# Make sure protocol is valid
		assert protocol, "Protocol is not valid"

		# Create socket using the protocol
		stream = socket.socket(protocol, socket.SOCK_STREAM)

		# Bind and connect using addresses
		stream.bind(source)
		stream.connect(destination)
		
		# Wrap with all socket wrappers
		for wrapper in wrappers:
			stream = wrapper(stream)

		# Return created socket
		return stream, source, destination

	def connect(self, source=None, destination=None, secure=False, *wrappers):
		# Make sure browser is not connected already
		assert not self.connected, "Browser is already connected"

		# Connect to destination
		self._socket, self._source, self._destination = self.socket(source, destination, self._protocol, *[])


class Request(object):
	pass

class Response(object):
	pass

class Wrapper(object):
	pass