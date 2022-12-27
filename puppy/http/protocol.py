# Import socket utilities
from puppy.socket.wrapper import SocketWrapper, SocketReader, SocketWriter

# Import required types
from puppy.http.types import Received, Request, Response, Headers
from puppy.http.constants import (
    CRLF,
    INTEGER,
    SPEARATOR,
    WHITESPACE,
    CHUNKED,
    CONTENT_TYPE,
    CONTENT_LENGTH,
    TRANSFER_ENCODING,
)


class HTTPSocket(SocketWrapper):

    def __init__(self, *args, **kwargs):
        # Initialize the parent
        super(HTTPSocket, self).__init__(*args, **kwargs)

        # Set the default separator
        self._separator = CRLF


class HTTPReader(HTTPSocket, SocketReader):

    def receive_artifact(self):
        # Receive all artifact components
        header = self.readline()
        headers = self.receive_headers()
        content = self.receive_content(headers)

        # Return created artifact
        return Received(header, headers, content)

    def receive_headers(self):
        # Create headers object
        headers = Headers()

        # Loop over all lines
        for line in self.readlines():
            # Validate header structure
            if SPEARATOR not in line:
                continue

            # Split header line and create object
            name, value = line.split(SPEARATOR, 1)
            name, value = name.strip(), value.strip()

            # Yield new header
            headers.append(name, value)

        # Return the headers object
        return headers

    def receive_content(self, headers):
        # If a length is defined, fetch by length
        if headers.has(CONTENT_LENGTH):
            # Fetch content-length header
            (content_length,) = headers.pop(CONTENT_LENGTH)

            # Read content by known length
            return self.receive_content_by_length(int(content_length))

        # If encoding is defined, fetch by chunks
        if headers.has(TRANSFER_ENCODING):
            # Fetch transfer-encoding header
            (transfer_encoding,) = headers.pop(TRANSFER_ENCODING)

            # Make sure the encoding is supported
            assert transfer_encoding.lower() == CHUNKED

            # Receive by chunks
            return self.receive_content_by_chunks()

        # Make sure content-type is defined
        if not headers.has(CONTENT_TYPE):
            return

        # Make sure connection is defined
        if not headers.has(CONNECTION):
            return

        # Make sure connection will close
        for connection in headers.get(CONNECTION):
            if connection.lower() != CLOSE:
                return

        # Receive content until socket is closed
        return self.receive_content_by_stream()

    def receive_content_by_length(self, length):
        return self.recvexact(length)

    def receive_content_by_chunks(self):
        # Initialize buffer and length
        length = None
        buffer = bytes()

        # Loop until length is 0
        while length != 0:
            # Receive the next chunk's length
            length = int(self.readline(), 16)

            # Yield the line's length
            buffer += self.recvexact(length)

            # Read separator line
            self.readline()

        # Return created buffer
        return buffer

    def receive_content_by_stream(self):
        # Receive all data
        return self.recvall()


class HTTPWriter(HTTPSocket, SocketWriter):

    def transmit_artifact(self, artifact):
        # Transmit all parts
        self.writeline(artifact.header)
        self.transmit_headers(artifact.headers)
        self.transmit_content(artifact.content)

    def transmit_header(self, name, value):
        # Write header in "key: value" format
        self.writeline(name + SPEARATOR + WHITESPACE + value)

    def transmit_headers(self, headers):
        # Loop over headers and transmit them
        for name, value in headers:
            self.transmit_header(name, value)

    def transmit_content(self, content):
        # Make sure content is defined
        content = content or bytes()

        # Write content-length header
        self.transmit_header(CONTENT_LENGTH, INTEGER % len(content))

        # Write HTTP separator
        self.writeline()

        # Send content as is
        self.sendall(content)


class HTTPReceiver(HTTPReader):

    def receive_request(self):
        # Receive artifact from parent
        artifact = self.receive_artifact()

        # Parse HTTP header as request header
        method, location, _ = artifact.header.split(WHITESPACE, 2)

        # Return created request
        return Request(method, location, artifact.headers, artifact.content)

    def receive_response(self):
        # Receive artifact from parent
        artifact = self.receive_artifact()

        # Parse HTTP header as response header
        _, status, message = artifact.header.split(WHITESPACE, 2)

        # Convert status to int
        status = int(status)

        # Return created response
        return Response(status, message, artifact.headers, artifact.content)


class HTTPTransmitter(HTTPWriter):

    def transmit_request(self, request):
        return self.transmit_artifact(request)

    def transmit_response(self, response):
        return self.transmit_artifact(response)
