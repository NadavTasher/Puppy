# Import socket utilities
from puppy.socket.io import SocketReader, SocketWriter

# Import required types
from puppy.http.types import Received, Request, Response, Headers
from puppy.http.constants import (
    CHUNKED,
    CONTENT_TYPE,
    CONTENT_LENGTH,
    TRANSFER_ENCODING,
)


class HTTPReader(SocketReader):
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
            if ":" not in line:
                continue

            # Split header line and create object
            name, value = line.split(":", 1)

            # Yield new header
            headers.append(name.strip(), value.strip())

        # Return the headers object
        return headers

    def receive_content(self, headers):
        # If a length is defined, fetch by length
        if headers.has(CONTENT_LENGTH):
            # Fetch content-length header
            (content_length,) = headers.pop(CONTENT_LENGTH)

            # Read content by known length
            return self.receive_content_by_length(int(content_length.decode()))

        # If encoding is defined, fetch by chunks
        if headers.has(TRANSFER_ENCODING):
            # Fetch transfer-encoding header
            (transfer_encoding,) = headers.pop(TRANSFER_ENCODING)

            # Make sure the encoding is supported
            assert transfer_encoding.decode().lower() == CHUNKED

            # Receive by chunks
            return self.receive_content_by_chunks()

        # If a content type is defined, receive by stream
        if headers.has(CONTENT_TYPE):
            return self.receive_content_by_stream()

    def receive_content_by_length(self, length):
        return self.recvexact(length)

    def receive_content_by_chunks(self):
        # Initialize buffer and length
        length = None
        buffer = bytearray()

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


class HTTPWriter(SocketWriter):
    def transmit_artifact(self, artifact):
        # Transmit all parts
        self.writeline(artifact.header)
        self.transmit_headers(artifact.headers)
        self.transmit_content(artifact.content)

    def transmit_header(self, name, value):
        # Write header in "key: value" format
        self.writeline("%s: %s" % (name, value))

    def transmit_headers(self, headers):
        # Loop over headers and transmit them
        for name, value in headers:
            self.transmit_header(name, value)

    def transmit_content(self, content):
        if content:
            # Write content-length header
            self.transmit_header(CONTENT_LENGTH, str(len(content)))

            # Write HTTP separator
            self.writeline()

            # Send content as is
            self.send(content)
        else:
            # Write double HTTP separator
            self.writeline()
            self.writeline()


class HTTPReceiver(HTTPReader):
    def receive_request(self):
        # Receive artifact from parent
        artifact = self.receive_artifact()

        # Parse HTTP header as request header
        method, location, _ = artifact.header.split(None, 2)

        # Return created request
        return Request(method, location, artifact.headers, artifact.content)

    def receive_response(self):
        # Receive artifact from parent
        artifact = self.receive_artifact()

        # Parse HTTP header as response header
        _, status, message = artifact.header.split(None, 2)

        # Convert status to int
        status = int(status)

        # Return created response
        return Response(status, message, artifact.headers, artifact.content)


class HTTPTransmitter(HTTPWriter):
    def transmit_request(self, request):
        return self.transmit_artifact(request)

    def transmit_response(self, response):
        return self.transmit_artifact(response)