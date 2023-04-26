import ssl

from puppy.simple.http import SafeHTTP
from puppy.socket.server import SocketServer, SocketWorker


class HTTPWorker(SocketWorker):

    interface = None

    def initialize(self):
        # Create the HTTP interface
        self.interface = SafeHTTP()

    def handle(self):
        try:
            # Read request from client
            request = self.interface.receive_request(self.socket)

            # Handle client request
            response = self.parent.handler(request)

            # Transmit response to client
            self.interface.transmit_response(self.socket, response)
        except IOError:
            # Stop the worker
            raise KeyboardInterrupt()


class HTTPSWorker(HTTPWorker):

    def initialize(self):
        # Initialize the handler
        super(HTTPSWorker, self).initialize()

        try:
            # Wrap socket with SSL using parent's context
            self.socket = self.parent.context.wrap_socket(self.socket, server_side=True)
        except (ssl.SSLError, OSError):
            # Raise exception to stop the handler
            raise KeyboardInterrupt()


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
