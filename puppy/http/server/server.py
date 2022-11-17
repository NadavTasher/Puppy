# Import python modules
import socket  # NOQA
import select  # NOQA

from puppy.http.http import HTTP  # NOQA
from puppy.socket.server import ThreadingTCPServer, StreamRequestHandler  # NOQA


class HTTPWorker(StreamRequestHandler, object):
    def handle(self):
        # Create an interface from the socket
        interface = HTTP(self.request)

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


class HTTPServer(ThreadingTCPServer, object):
    def __init__(self, address, handler):
        # Set the handler
        self.handler = handler

        # Initialize parent
        super(HTTPServer, self).__init__(address, HTTPWorker)
