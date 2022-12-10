import ssl
import socket
import contextlib

from puppy.http.http import HTTP
from puppy.http.mixins import HTTPSafeReceiverMixIn

from puppy.socket.server import SocketServer, SocketWorker


@contextlib.contextmanager
def supress_socket_errors():
    try:
        # Yield for execution
        yield
    except socket.error as exception:
        pass


@contextlib.contextmanager
def supress_certificate_errors():
    try:
        # Yield for execution
        yield
    except ssl.SSLError as exception:
        # Check if message should be ignored
        if not any(message in str(exception) for message in ["ALERT_CERTIFICATE_UNKNOWN"]):
            raise


class HTTPClass(HTTP, HTTPSafeReceiverMixIn):
    pass


class HTTPHandler(SocketWorker):
    # Internal HTTP interface
    _interface = None

    def run(self):
        # Run loop with exception handlers
        with supress_socket_errors():
            super(HTTPHandler, self).run()

    def loop(self):
        # Check if interface was closed
        if self._interface.closed:
            self.stop()
            return

        # Check if interface is readable
        if not self._interface.wait(1):
            return

        # Read request from client
        request = self._interface.receive_request()

        # Handle client request
        response = self._parent.handler(request)

        # Transmit response to client
        self._interface.transmit_response(response)


class HTTPWorker(HTTPHandler):

    def initialize(self):
        # Initialize parent
        super(HTTPWorker, self).initialize()

        # Initialize the interface
        self._interface = HTTPClass(self._socket)


class HTTPSWorker(HTTPHandler):

    def run(self):
        # Run loop with exception handlers
        with supress_certificate_errors():
            super(HTTPSWorker, self).run()

    def initialize(self):
        # Initialize parent
        super(HTTPSWorker, self).initialize()

        # Wrap socket with SSL using parent's context
        self._socket = self._parent.context.wrap_socket(self._socket, server_side=True)

        # Initialize the interface
        self._interface = HTTPClass(self._socket)


class HTTPServer(SocketServer):

    def __init__(self, handler, http=80, https=443):
        # Initialize looper
        super(HTTPServer, self).__init__({("0.0.0.0", http): HTTPWorker, ("0.0.0.0", https): HTTPSWorker})

        # Set the handler
        self.handler = handler

        # Initialize SSL context
        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_OPTIONAL