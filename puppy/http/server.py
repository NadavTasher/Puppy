import ssl

from puppy.simple.http import SafeHTTP
from puppy.socket.server import SocketServer, SocketWorker


class HTTPHandler(SocketWorker):
    # Internal HTTP interface
    _class = SafeHTTP
    _interface = None

    def loop(self):
        # Check if interface was closed
        if self._interface.closed:
            raise KeyboardInterrupt()

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
        HTTPHandler.initialize(self)

        # Initialize the interface
        self._interface = self._class(self._socket)


class HTTPSWorker(HTTPHandler):

    def initialize(self):
        # Initialize parent
        HTTPHandler.initialize(self)

        try:
            # Wrap socket with SSL using parent's context
            self._socket = self._parent.context.wrap_socket(self._socket, server_side=True)
        except (ssl.SSLError, OSError):
            # Raise exception to stop the handler
            raise KeyboardInterrupt()

        # Initialize the interface
        self._interface = self._class(self._socket)


class HTTPServer(SocketServer):

    def __init__(self, handler, http=80, https=443):
        # Initialize looper
        super(HTTPServer, self).__init__({("0.0.0.0", http): HTTPWorker, ("0.0.0.0", https): HTTPSWorker})

        # Set the handler
        self.handler = handler

        # Initialize SSL context
        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE
