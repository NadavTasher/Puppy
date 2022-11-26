import ssl  # NOQA
import socket  # NOQA
import select  # NOQA

from puppy.http.http import HTTP  # NOQA
from puppy.http.mixins import HTTPSafeReceiverMixIn  # NOQA
# from puppy.socket.server import SocketServer, SocketWorker

from puppy.thread.looper import Looper


class HTTPClass(HTTP, HTTPSafeReceiverMixIn):
    pass


class MultiHTTPWorker(Looper):
    def __init__(self, server, handler, context=None):
        # Initialize the looper
        super(MultiHTTPWorker, self).__init__()
        
        # Set daemon to true
        self.daemon = True

        # Set the internal state
        self._socket = None
        self._interface = None

        # Set internal constants
        self._server = server
        self._handler = handler
        self._context = context

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
        response = self._handler(request)

        # Transmit response to client
        self._interface.transmit_response(response)

    def initialize(self):
        # Accept a client
        self._socket, address = self._server.accept()

        # Set the internal name
        self.name = "%s:%d" % address

        # If a context was defined, wrap socket
        if self._context:
            self._socket = self._context.wrap_socket(self._socket, server_side=True)

        # Initialize the interface
        self._interface = HTTPClass(self._socket)

    def finalize(self):
        # Close socket if needed
        if self._socket:
            self._socket.close()


class MultiHTTPServer(Looper):
    def __init__(self, handler, http_port=80, https_port=443):
        # Initialize looper
        super(MultiHTTPServer, self).__init__()

        # Set daemon to true
        self.daemon = True

        # Set internal variables
        self._handler = handler
        self._http_port = http_port
        self._https_port = https_port

        # Initialize sockets for listening
        self._http_socket = None
        self._https_socket = None

        # Initialize ssl context
        self._context = ssl.create_default_context()
        self._context.check_hostname = False
        self._context.verify_mode = ssl.CERT_OPTIONAL

    @property
    def context(self):
        return self._context

    def loop(self):
        # Check which sockets are readable
        readable_sockets, _, _ = select.select([self._http_socket, self._https_socket], [], [], 0.5)

        # Loop over readable sockets and create client threads
        for readable_socket in readable_sockets:
            worker = MultiHTTPWorker(readable_socket, self._handler, self._context if readable_socket is self._https_socket else None)
            worker.start()

    def initialize(self):
        # Create HTTP socket for listening
        self._http_socket = socket.socket()
        self._http_socket.bind(("0.0.0.0", self._http_port))
        self._http_socket.listen(1)

        # Create HTTPS socket for listening
        self._https_socket = socket.socket()
        self._https_socket.bind(("0.0.0.0", self._https_port))
        self._https_socket.listen(1)

    def finalize(self):
        # Close HTTP socket if needed
        if self._http_socket:
            self._http_socket.close()

        # Close HTTPS socket if needed
        if self._https_socket:
            self._https_socket.close()
