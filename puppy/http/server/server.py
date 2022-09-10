# Import python modules
import socket
import select

# Import protocol classes
from ..http import *

# Import looper classes
from ...thread import SocketServer, SocketWorker


class Worker(SocketWorker):
	def __init__(self, parent, handler):
		# Set internal parameters
		self._handler = handler
		self._interface = None

		# Initialize looper class
		super(Worker, self).__init__(parent)

	def initialize(self):
		# Initialize parent
		super(Worker, self).initialize()

		# Create HTTP interface
		self._interface = HTTPServerWrapper(
			HTTPCompressionWrapper(
				HTTPConnectionStateWrapper(
					HTTPInterface(self._socket)
				)
			)
		)

	def handle(self):
		# Receive request, handle, response
		self._interface.transmit(self._handler(self._interface.receive()))

	# @property
	# def running(self):
	#     # Check if socket is closed
	#     return super(Worker, self).running and not self._socket._closed

class Server(SocketServer):
	def __init__(self, address, handler):
		# Set handler function
		self._handler = handler

		# Initialize looper class
		super(Server, self).__init__(address)

	def child(self):
		return Worker(self, self._handler)
