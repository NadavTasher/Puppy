import io

from puppy.http.protocol import HTTPReceiver, HTTPTransmitter
from puppy.http.constants import CR, LF

from puppy.socket.utilities import readuntil


class HTTPCompatibleReceiverMixIn(HTTPReceiver):

    def receive_line(self, socket):
        # Read until LF in buffer
        line = readuntil(socket, LF)

        # Make sure buffer is not empty
        if not line:
            return line

        # Check if CR should be stripped
        if line[-len(CR)] != CR:
            return line

        # Return the modified buffer
        return line[:-len(CR)]


class HTTPBufferedTransmitterMixIn(HTTPTransmitter):

    buffer = None

    def transmit_artifact(self, socket, artifact):
        # Create temporary writing buffer
        buffer = io.BytesIO()

        try:

            # Transmit the artifact using the parent
            return super(HTTPBufferedTransmitterMixIn, self).transmit_artifact(buffer, artifact)
        finally:
            # Write the buffer
            write(socket, buffer.getvalue())
