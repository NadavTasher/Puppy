# Import python modules
import socket
import select

# Import protocol classes
from ..protocol import header
from ..handlers import Server as ServerHandler

# Import looper classes
from ...thread import Server as SocketServer, Worker as SocketWorker


class Worker(SocketWorker):
	def __init__(self, parent, handler):
		# Set internal parameters
		self._close = None
		self._handler = handler

		# Initialize looper class
		super(Worker, self).__init__(parent)

	def handle(self):
		# Receive request, handle, response
		self.transmit(self._handler(self.receive()))

	def receive(self):
		# Receive a request on the socket
		request = ServerHandler.receive(self._socket)

		# Check connection state header
		connection = header("Connection", request.headers)

		# Check if connection state header was set
		if not connection:
			# Default - close connection
			self._close = True
		else:
			# Compare header to known close value
			self._close = connection.lower() == "close"

		# Return received request
		return request

	def transmit(self, response):
		# Create new response headers
		headers = [
			# Close if connection should be closed, keep-alive otherwise
			Header("Connection", "close" if self._close else "keep-alive")
		] + response.headers

		# Create new response (replace parameter)
		response = response._replace(headers=headers)

		# Transmit response on the socket
		ServerHandler.transmit(self._socket, response)

		# Stop worker if needed
		if self._close:
			self.stop()


class Server(SocketServer):
	def __init__(self, address, handler):
		# Set handler function
		self._handler = handler

		# Initialize looper class
		super(Server, self).__init__(address, self.child)

	def child(self, parent):
		return Worker(parent, self._handler)
