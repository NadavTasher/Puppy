# Import python modules
import socket
import select

# Import protocol classes
from ..http import HTTPInterface, HTTPServerWrapper, HTTPCompressionWrapper, HTTPConnectionStateWrapper

# Import looper classes
from ...thread import Server, Worker


class HTTPWorker(Worker):
	def __init__(self, handler):
		# Set internal parameters
		self._handler = handler
		self._interface = None

		# Initialize looper class
		super(HTTPWorker, self).__init__()

	def initialize(self):
		# Initialize parent
		super(HTTPWorker, self).initialize()

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

	# TODO: add this

	# @property
	# def running(self):
	#     # Check if socket is closed
	#     return super(Worker, self).running and not self._socket._closed

class HTTPServer(Server):
	def __init__(self, address, handler):
		# Set handler function
		self._handler = handler

		# Initialize looper class
		super(HTTPServer, self).__init__(address)

	def child(self):
		return HTTPWorker(self._handler).adopt(self)
