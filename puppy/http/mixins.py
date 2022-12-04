import io  # NOQA
import gzip  # NOQA

from puppy.http.protocol import HTTPReceiver, HTTPTransmitter  # NOQA
from puppy.http.constants import (
    HOST,
    GZIP,
    CLOSE,
    CONNECTION,
    ACCEPT_ENCODING,
    CONTENT_ENCODING,
)  # NOQA

from puppy.socket.wrapper import SocketWrapper, CRLF  # NOQA


class HTTPGzipMixIn(SocketWrapper):
    # Internal supported variable
    compression_support = False


class HTTPGzipReceiverMixIn(HTTPGzipMixIn, HTTPReceiver):
    def receive_artifact(self):
        # Read artifact from parent
        artifact = super(HTTPGzipReceiverMixIn, self).receive_artifact()

        # Update compression support from artifact
        self._update_compression_support(artifact.headers)

        # Check if a content encoding was supplied
        if not artifact.headers.has(CONTENT_ENCODING):
            return artifact

        # Check the content encoding
        (content_encoding,) = artifact.headers.pop(CONTENT_ENCODING)

        # Make sure that the gzip encoding was provided
        assert content_encoding.lower() == GZIP

        # Decompress content as gzip
        with gzip.GzipFile(
            fileobj=io.BytesIO(artifact.content), mode="rb"
        ) as decompressor:
            artifact.content = decompressor.read()

        # Return the artifact
        return artifact

    def _update_compression_support(self, headers):
        # Update compression support to false
        self.compression_support = False

        # Fetch the accepted encodings
        if not headers.has(ACCEPT_ENCODING):
            return

        # Split the header value and loop
        for accepted_encodings in headers.fetch(ACCEPT_ENCODING):
            for encoding in accepted_encodings.split(b","):
                if encoding.strip().lower() == GZIP:
                    # Compression is supported!
                    self.compression_support = True


class HTTPGzipTransmitterMixIn(HTTPGzipMixIn, HTTPTransmitter):
    def transmit_request(self, request):
        # Add accept-encoding header
        request.headers.update(ACCEPT_ENCODING, GZIP)

        # Transmit modified request
        return super(HTTPGzipTransmitterMixIn, self).transmit_request(request)

    def transmit_response(self, response):
        # Check if compression is supported
        if self.compression_support and response.content:
            # Add compression header
            response.headers.append(CONTENT_ENCODING, GZIP)

            # Compress the content using gzip
            temporary = io.BytesIO()
            with gzip.GzipFile(fileobj=temporary, mode="w") as compressor:
                compressor.write(response.content)

            # Update content with value
            response.content = temporary.getvalue()

        # Transmit the response
        return super(HTTPGzipTransmitterMixIn, self).transmit_response(response)


class HTTPConnectionStateMixIn(SocketWrapper):
    # Internal close variable
    should_close = False


class HTTPConnectionStateReceiverMixIn(HTTPConnectionStateMixIn, HTTPReceiver):
    def receive_artifact(self):
        # Receive artifact from headers
        artifact = super(HTTPConnectionStateReceiverMixIn, self).receive_artifact()

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
        if not headers.has(CONNECTION):
            return

        # Fetch connection header
        (connection,) = headers.fetch(CONNECTION)

        # Compare header to keepalive
        self.should_close = connection.lower() == CLOSE


class HTTPConnectionStateTransmitterMixIn(HTTPConnectionStateMixIn, HTTPTransmitter):
    def transmit_artifact(self, artifact):
        # Add connection state header
	if self.should_close:
	    artifact.headers.update(CONNECTION, CLOSE)

        # Write the artifact
        return super(HTTPConnectionStateTransmitterMixIn, self).transmit_artifact(
            artifact
        )

    def transmit_response(self, response):
        # Try-finally
        try:
            return super(HTTPConnectionStateTransmitterMixIn, self).transmit_response(
                response
            )
        finally:
            # Close the socket if needed
            if self.should_close:
                self.close()


class HTTPHostTransmitterMixIn(HTTPTransmitter):
    # Set internal host variable
    host = None

    def transmit_request(self, request):
        # Create host variable with global
        host = self.host

        # Make sure host header is defined
        if not host:
            # Get IP from peername
            host, _ = self._socket.getpeername()

        # Update the request with the appropriate header
        request.headers.update(HOST, host)

        # Transmit the request
        return super(HTTPHostTransmitterMixIn, self).transmit_request(request)


class HTTPSafeReceiverMixIn(HTTPReceiver):
    # Variables to determine maximum sizes
    maximum_readline = 4 * 1024
    maximum_recvall = 4 * 1024 * 1024
    maximum_recvexact = 64 * 1024 * 1024

    def recvexact(self, length=0):
        # Make sure the length is not larger then maxlength
        assert length < self.maximum_recvexact, "Chunk is too long"

        # Receive using parent
        return super(HTTPSafeReceiverMixIn, self).recvexact(length)

    def recvall(self):
        # Initialize reading buffer
        buffer = bytes()
        temporary = True

        # Loop until nothing left to read
        while temporary:
            # Make sure buffer is not too long
            assert len(buffer) < self.maximum_recvall, "Buffer is too long"

            # Read new temporary chunk
            temporary = self.recv(self._chunk)

            # Append chunk to buffer
            buffer += temporary

        # Return the buffer
        return buffer

    def readline(self):
        # Create a reading buffer
        buffer = bytes()

        # Loop until CRLF in buffer
        while self._separator not in buffer:
            # Make sure buffer is not too long
            assert len(buffer) < self.maximum_readline, "Line is too long"

            # Read and append to buffer
            buffer += self.recvexact(1)

        # Return the buffer without the CRLF
        return buffer[: -len(self._separator)]
