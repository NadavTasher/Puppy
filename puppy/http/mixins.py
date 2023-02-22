import io
import gzip

from puppy.http.protocol import HTTPReceiver, HTTPTransmitter
from puppy.http.constants import (
    CR,
    LF,
    CRLF,
    INTEGER,
    HOST,
    GZIP,
    CLOSE,
    CONNECTION,
    ACCEPT_ENCODING,
    CONTENT_ENCODING,
)

from puppy.socket.wrapper import SocketWrapper


class HTTPGzipMixIn(SocketWrapper):
    compression_support = False


class HTTPGzipReceiverMixIn(HTTPGzipMixIn, HTTPReceiver):

    def receive_artifact(self, *args, **kwargs):
        # Read artifact from parent
        artifact = super(HTTPGzipReceiverMixIn, self).receive_artifact(*args, **kwargs)

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
        with gzip.GzipFile(fileobj=io.BytesIO(artifact.content), mode="rb") as decompressor:
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
        for accepted_encodings in headers.get(ACCEPT_ENCODING):
            for encoding in accepted_encodings.split(b","):
                if encoding.strip().lower() == GZIP:
                    # Compression is supported!
                    self.compression_support = True


class HTTPGzipTransmitterMixIn(HTTPGzipMixIn, HTTPTransmitter):

    def transmit_request(self, request):
        # Add accept-encoding header
        request.headers.set(ACCEPT_ENCODING, GZIP)

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
        if not headers.has(CONNECTION):
            return

        # Fetch connection header
        (connection,) = headers.get(CONNECTION)

        # Compare header to keepalive
        self.should_close = connection.lower() == CLOSE


class HTTPConnectionStateTransmitterMixIn(HTTPConnectionStateMixIn, HTTPTransmitter):

    def transmit_artifact(self, artifact):
        # Add connection state header
        if self.should_close:
            artifact.headers.set(CONNECTION, CLOSE)

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


class HTTPHostTransmitterMixIn(HTTPTransmitter):

    def transmit_request(self, request):
        # Make sure no host header is defined
        if not request.headers.has(HOST):
            return super(HTTPHostTransmitterMixIn, self).transmit_request(request)

        # Get host from peername and encode
        host, port = self._socket.getpeername()

        # Update the request with the appropriate header
        request.headers.set(HOST, host.encode() + b":" + INTEGER % port)

        # Transmit the request
        return super(HTTPHostTransmitterMixIn, self).transmit_request(request)


class HTTPSafeReceiverMixIn(HTTPReceiver):
    # Variables to determine maximum sizes
    maximum_readline = 4 * 1024
    maximum_recvall = 4 * 1024 * 1024
    maximum_recvexact = 64 * 1024 * 1024

    def __init__(self, wrapped, timeout=60):
        # Initialize parent
        super(HTTPSafeReceiverMixIn, self).__init__(wrapped)

        # Set a socket timeout
        self._socket.settimeout(timeout)

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
        return buffer[:-len(self._separator)]


class HTTPCompatibleReceiverMixIn(HTTPReceiver):

    def readline(self):
        # Create a reading buffer
        buffer = bytes()

        # Loop until CRLF in buffer
        while LF not in buffer:
            # Read and append to buffer
            buffer += self.recvexact(1)

        # Strip the LF from the buffer
        buffer = buffer[:-len(LF)]

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

    def sendall(self, buffer):
        # Add to buffer using send
        self.send(buffer)

        # Flush the buffer
        self.flush()

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
