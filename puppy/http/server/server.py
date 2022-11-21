import ssl  # NOQA
import socket  # NOQA
import select  # NOQA

from puppy.http.http import HTTP  # NOQA
from puppy.http.mixins import HTTPSafeReceiverMixIn  # NOQA
from puppy.socket.server import ThreadingTCPServer, StreamRequestHandler  # NOQA


class HTTPClass(HTTP, HTTPSafeReceiverMixIn):
    pass


class HTTPWorker(StreamRequestHandler, object):
    def handle(self):
        # Create an interface from the socket
        interface = HTTPClass(self.request)

        # Loop until interface is closed
        try:
            while not interface.closed:
                # Check if interface is readable
                if not interface.wait(1):
                    continue

                # Read request from client
                request = interface.receive_request()

                # Handle client request
                response = self.server.handler(request)

                # Transmit response to client
                interface.transmit_response(response)
        except:
            # Abort the connection
            interface.abort()
        finally:
            # Close the interface
            interface.close()


class HTTPSWorker(HTTPWorker):
    def handle(self):
        # Wrap with TLS implementation
        self.request = self.server.context.wrap_socket(self.request, server_side=True)

        # Handle using parent
        return super(HTTPSWorker, self).handle()


class HTTPServer(ThreadingTCPServer, object):
    def __init__(self, address, handler):
        # Set the handler
        self.handler = handler

        # Initialize parent
        super(HTTPServer, self).__init__(address, HTTPWorker)


class HTTPSServer(ThreadingTCPServer, object):
    def __init__(self, address, handler):
        # Set the handler
        self.handler = handler

        # Create a new context
        self.context = ssl.create_default_context()
        self.context.check_hostname = False

        # Initialize parent
        super(HTTPSServer, self).__init__(address, HTTPSWorker)
