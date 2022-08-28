# Import python modules
import socket
import select

# Import protocol classes
from ..handler import _Server

# Import looper classes
from ...looper import Looper

class Server(Looper):
	def __init__(self, address, handler):
		# Initialize looper class
		Looper.__init__(self)

		# Set internal parameters
		self._socket = None
		self._address = address
		self._handler = handler

	def loop(self):
		pass

	def initialize(self):
		# Create socket to listen on
		self._socket = socket.socket()
		self._socket.bind(self._address)
		self._socket.listen(10)

	def finalize(self):
		# Close the listening socket
		if not self._socket:
			return
		
		# Close socket
		self._socket.close()
		self._socket = None

class Worker(Looper):
	# Internal variables
	_socket = None

	def handle(self):
		pass

	def loop(self):
		# Check if there is data on the socket
		has_data, _, _ = select.select([self._socket], [], [], 1)

		# Make sure socket has data
		if not has_data:
			return

		# Handle request on socket
		self.handle()


	def initialize(self):
		# Accept a socket from the parent
		self._socket, _ = self._parent._socket.accept()

	def finalize(self):
		# Make sure connection is set
		if not self._socket:
			return

		# Close connection
		self._socket.close()
		self._socket = None