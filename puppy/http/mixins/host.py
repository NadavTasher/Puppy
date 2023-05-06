from puppy.http.protocol import HTTPTransmitter
from puppy.http.constants import INTEGER, HOST
from puppy.http.utilities import set_header, has_header


class HTTPHostTransmitterMixIn(HTTPTransmitter):

    def transmit_request(self, socket, request):
        # Make sure no host header is defined
        if has_header(request.headers, HOST):
            return super(HTTPHostTransmitterMixIn, self).transmit_request(socket, request)

        # Get host from peername and encode
        host, port = socket.getpeername()

        # Update the request with the appropriate header
        set_header(request.headers, HOST, host.encode() + b":" + INTEGER % port)

        # Transmit the request
        return super(HTTPHostTransmitterMixIn, self).transmit_request(socket, request)
