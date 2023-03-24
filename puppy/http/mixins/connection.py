from puppy.socket.wrapper import SocketWrapper
from puppy.http.protocol import HTTPReceiver, HTTPTransmitter
from puppy.http.constants import CLOSE, CONNECTION


class HTTPConnectionStateMixIn(SocketWrapper):
    should_close = False


class HTTPConnectionStateReceiverMixIn(HTTPConnectionStateMixIn, HTTPReceiver):

    def receive_artifact(self, *args, **kwargs):
        # Receive artifact from headers
        artifact = super(HTTPConnectionStateReceiverMixIn, self).receive_artifact(*args, **kwargs)

        # Update connection state
        self._update_connection_state(artifact.headers)

        # Return the artifact
        return artifact

    def receive_response(self):
        # Try-finally
        try:
            return super(HTTPConnectionStateReceiverMixIn, self).receive_response()
        finally:
            # Close the socket if needed
            if self.should_close:
                self.close()

    def _update_connection_state(self, headers):
        # Set default should close
        self.should_close = True

        # If connection header not present, return
        if CONNECTION not in headers:
            return

        # Fetch connection header
        (connection,) = headers[CONNECTION]

        # Compare header to keepalive
        self.should_close = connection.lower() == CLOSE


class HTTPConnectionStateTransmitterMixIn(HTTPConnectionStateMixIn, HTTPTransmitter):

    def transmit_artifact(self, artifact):
        # Add connection state header
        if self.should_close:
            artifact.headers[CONNECTION] = CLOSE

        # Write the artifact
        return super(HTTPConnectionStateTransmitterMixIn, self).transmit_artifact(artifact)

    def transmit_response(self, response):
        # Try-finally
        try:
            return super(HTTPConnectionStateTransmitterMixIn, self).transmit_response(response)
        finally:
            # Close the socket if needed
            if self.should_close:
                self.close()
