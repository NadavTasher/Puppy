from puppy.http.protocol import HTTPTransmitter
from puppy.http.constants import INTEGER, HOST


class HTTPHostTransmitterMixIn(HTTPTransmitter):

    def transmit_request(self, socket, request):
        # Make sure no host header is defined
        if HOST in request.headers:
            return super(HTTPHostTransmitterMixIn, self).transmit_request(socket, request)

        # Get host from peername and encode
        host, port = socket.getpeername()

        # Update the request with the appropriate header
        request.headers[HOST] = host.encode() + b":" + INTEGER % port

        # Transmit the request
        return super(HTTPHostTransmitterMixIn, self).transmit_request(socket, request)
