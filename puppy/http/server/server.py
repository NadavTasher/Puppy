import ssl  # NOQA
import socket  # NOQA
import select  # NOQA

from puppy.http.http import HTTP  # NOQA
from puppy.http.mixins import HTTPSafeReceiverMixIn  # NOQA

# from puppy.socket.server import SocketServer, SocketWorker

from puppy.thread.looper import Looper
from puppy.socket.server import SocketServer, SocketWorker  # NOQA


class HTTPClass(HTTP, HTTPSafeReceiverMixIn):
    pass


class HTTPHandler(SocketWorker):
    # Internal HTTP interface
    _interface = None

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
        response = self._parent._handler(request)

        # Transmit response to client
        self._interface.transmit_response(response)


class HTTPWorker(HTTPHandler):
    def initialize(self):
        # Initialize parent
        super(HTTPWorker, self).initialize()

        # Initialize the interface
        self._interface = HTTPClass(self._socket)


class HTTPSWorker(HTTPHandler):
    def initialize(self):
        # Initialize parent
        super(HTTPSWorker, self).initialize()

        # Wrap socket with SSL using parent's context
        self._socket = self._parent.context.wrap_socket(self._socket, server_side=True)

        # Initialize the interface
        self._interface = HTTPClass(self._socket)


# class HTTPWorker(Looper):
#     def __init__(self, server, handler, context=None):
#         # Initialize the looper
#         super(HTTPWorker, self).__init__()

#         # Set daemon to true
#         self.daemon = True

#         # Set the internal state
#         self._socket = None
#         self._interface = None

#         # Set internal constants
#         self._server = server
#         self._handler = handler
#         self._context = context

#     def loop(self):
#         # Check if interface was closed
#         if self._interface.closed:
#             self.stop()
#             return

#         # Check if interface is readable
#         if not self._interface.wait(1):
#             return

#         # Read request from client
#         request = self._interface.receive_request()

#         # Handle client request
#         response = self._handler(request)

#         # Transmit response to client
#         self._interface.transmit_response(response)

#     def initialize(self):
#         # Accept a client
#         self._socket, address = self._server.accept()

#         # Set the internal name
#         self.name = "%s:%d" % address

#         # If a context was defined, wrap socket
#         if self._context:
#             self._socket = self._context.wrap_socket(self._socket, server_side=True)

#         # Initialize the interface
#         self._interface = HTTPClass(self._socket)

#     def finalize(self):
#         # Close socket if needed
#         if self._socket:
#             self._socket.close()


class HTTPServer(SocketServer):
    def __init__(self, handler, http=80, https=443):
        # Initialize looper
        super(HTTPServer, self).__init__(
            {("0.0.0.0", http): HTTPWorker, ("0.0.0.0", https): HTTPSWorker}
        )

        # Initialize ssl context
        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_OPTIONAL
