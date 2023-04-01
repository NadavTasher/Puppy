import io

from puppy.http.protocol import HTTPReceiver, HTTPTransmitter
from puppy.http.constants import CR, LF


class HTTPCompatibleReceiverMixIn(HTTPReceiver):

    def readline(self, *args, **kwargs):
        # Read until LF in buffer
        buffer = self.readuntil(LF)

        # Make sure buffer is not empty
        if not buffer:
            return buffer

        # Check if CR should be stripped
        if buffer[-len(CR)] != CR:
            return buffer

        # Return the modified buffer
        return buffer[:-len(CR)]


class HTTPBufferedTransmitterMixIn(HTTPTransmitter):

    buffer = None

    def transmit_artifact(self, artifact):
        try:
            # Transmit the artifact using the parent
            return super(HTTPBufferedTransmitterMixIn, self).transmit_artifact(artifact)
        finally:
            # Flush the buffer
            self.flush()

    def sendall(self, buffer):
        # Add to buffer using send
        self.send(buffer)

    def send(self, buffer):
        # Make sure buffer is initialized
        if not self.buffer:
            self.buffer = io.BytesIO()

        # Append data to buffer
        self.buffer.write(buffer)

    def flush(self):
        # Write the data using the parents' sendall
        super(HTTPBufferedTransmitterMixIn, self).sendall(self.buffer.getvalue())

        # Clear the buffer
        self.buffer = None
