# Import python modules
import socket  # NOQA
import select  # NOQA

from puppy.socket.server import Server, Worker  # NOQA
from puppy.http.server.interface import HTTPServerInterface  # NOQA


class HTTPWorker(Worker):
    # Private interface variable
    _interface = None

    def initialize(self):
        # Initialize parent
        super(HTTPWorker, self).initialize()

        # Create HTTP interface
        self._interface = HTTPServerInterface(self._socket)

    def handle(self):
        # Receive request, handle, response
        self._interface.transmit(self._parent._handler(self._interface.receive()))

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
        super(HTTPServer, self).__init__(address, HTTPWorker)
