from puppy.http.protocol import HTTPReceiver, HTTPTransmitter
from puppy.http.utilities import set_header, has_header, get_header
from puppy.http.constants import CLOSE, CONNECTION


class HTTPConnectionStateMixIn(object):
    should_close = False


class HTTPConnectionStateReceiverMixIn(HTTPConnectionStateMixIn, HTTPReceiver):

    def _receive_artifact(self, socket, content_expected=True):
        # Receive artifact from headers
        artifact = super(HTTPConnectionStateReceiverMixIn, self)._receive_artifact(socket, content_expected)

        # Update connection state
        self._update_connection_state(artifact.headers)

        # Return the artifact
        return artifact

    def receive_response(self, socket):
        # Try-finally
        try:
            return super(HTTPConnectionStateReceiverMixIn, self).receive_response(socket)
        finally:
            # Close the socket if needed
            if self.should_close:
                socket.close()

    def _update_connection_state(self, headers):
        # Set default should close
        self.should_close = True

        # If connection header not present, return
        if not has_header(headers, CONNECTION):
            return

        # Compare header to keepalive
        self.should_close = get_header(headers, CONNECTION).lower() == CLOSE


class HTTPConnectionStateTransmitterMixIn(HTTPConnectionStateMixIn, HTTPTransmitter):

    def _transmit_artifact(self, socket, artifact):
        # Add connection state header
        if self.should_close:
            set_header(artifact.headers, CONNECTION, CLOSE)

        # Write the artifact
        return super(HTTPConnectionStateTransmitterMixIn, self)._transmit_artifact(socket, artifact)

    def transmit_response(self, socket, response):
        # Try-finally
        try:
            return super(HTTPConnectionStateTransmitterMixIn, self).transmit_response(socket, response)
        finally:
            # Close the socket if needed
            if self.should_close:
                socket.close()
