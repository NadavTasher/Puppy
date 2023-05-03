import io

from puppy.http.protocol import HTTPReceiver, HTTPTransmitter
from puppy.http.constants import CR, LF, CRLF


class HTTPCompatibleReceiverMixIn(HTTPReceiver):

    def _receive_line(self, socket):
        # Read until LF in buffer
        line = self._receive_until(socket, LF)

        # Make sure buffer is not empty
        if not line:
            return line

        # Does line end with CRLF?
        if line[-len(CRLF):] == CRLF:
            return line[:-len(CRLF)]

        # Line does not end with CRLF
        return line[:-len(LF)]


class HTTPBufferedTransmitterMixIn(HTTPTransmitter):

    def _transmit(self, socket, buffer):
        # Write to the buffer
        socket.write(buffer)

    def _transmit_artifact(self, socket, artifact):
        # Create temporary writing buffer
        buffer = io.BytesIO()

        try:
            # Transmit the artifact to the buffer
            super(HTTPBufferedTransmitterMixIn, self)._transmit_artifact(buffer, artifact)
        finally:
            # Transmit the buffer
            super(HTTPBufferedTransmitterMixIn, self)._transmit(socket, buffer.getvalue())
