# Import python modules
import socket  # NOQA
import select  # NOQA

from puppy.http.http import HTTP  # NOQA
from puppy.socket.server import Server, Worker  # NOQA


class HTTPWorker(Worker):
    # Private interface variable
    _interface = None

    def initialize(self):
        # Initialize parent
        super(HTTPWorker, self).initialize()

        # Create HTTP interface
        self._interface = HTTP(self._socket)

    def handle(self):
        # Receive request, handle, response
        self._interface.transmit_response(
            self._parent._handler(self._interface.receive_request())
        )

    @property
    def running(self):
        # Check if socket is closed
        return super(HTTPWorker, self).running and not self._interface.closed


class HTTPServer(Server):
    def __init__(self, address, handler):
        # Set handler function
        self._handler = handler

        # Initialize looper class
        super(HTTPServer, self).__init__(address, HTTPWorker)
