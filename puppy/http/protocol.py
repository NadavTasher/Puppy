from puppy.http.headers import Headers
from puppy.http.request import Request
from puppy.http.response import Response
from puppy.http.artifact import Received
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

from puppy.socket.utilities import write, read, readall, readuntil


class HTTPReader(object):

    def receive_line(self, socket):
        return readuntil(socket, CRLF)

    def receive_lines(self, socket):
        # Initialize first line
        line = self.receive_line(socket)

        # Loop until no lines are left
        while line:
            # Yield the line
            yield line

            # Read the next line
            line = self.receive_line(socket)

    def receive_artifact(self, socket, content_expected=True):
        # Receive all artifact components
        header = self.receive_line(socket)
        headers = self.receive_headers(socket)
        content = self.receive_content(socket, headers, content_expected)

        # Return created artifact
        return Received(header, headers, content)

    def receive_headers(self, socket):
        # Create headers object
        headers = Headers()

        # Loop over all lines
        for line in self.receive_lines(socket):
            # Validate header structure
            if SPEARATOR not in line:
                continue

            # Split header line and create object
            name, value = line.split(SPEARATOR, 1)
            name, value = name.strip(), value.strip()

            # Append new header
            if name not in headers:
                headers[name] = value
            else:
                headers[name] += value

        # Return the headers object
        return headers

    def receive_content(self, socket, headers, content_expected=True):
        # If a length is defined, fetch by length
        if CONTENT_LENGTH in headers:
            # Fetch content-length header
            (content_length,) = headers.pop(CONTENT_LENGTH)

            # Read content by known length
            return self.receive_content_by_length(socket, int(content_length))

        # If encoding is defined, fetch by chunks
        if TRANSFER_ENCODING in headers:
            # Fetch transfer-encoding header
            (transfer_encoding,) = headers.pop(TRANSFER_ENCODING)

            # Make sure the encoding is supported
            assert transfer_encoding.lower() == CHUNKED

            # Receive content by chunks
            return self.receive_content_by_chunks(socket)

        # Make sure content-type is defined
        if CONTENT_TYPE not in headers:
            return

        # Make sure content is expected
        if not content_expected:
            return

        # Receive content until socket is closed
        return self.receive_content_by_stream(socket)

    def receive_content_by_length(self, socket, length):
        # Read content by known length
        return read(socket, length)

    def receive_content_by_chunks(self, socket):
        # Receive by chunks
        buffer = bytes()
        length = int(self.receive_line(socket), 16)

        # Loop until no more chunks
        while length:
            # Receive the chunk
            buffer += read(socket, length)

            # Read an empty line
            self.receive_line(socket)

            # Receive the next length
            length = int(self.receive_line(socket), 16)

        # Receive the last line
        self.receive_line(socket)

        # Return the buffer
        return buffer

    def receive_content_by_stream(self, socket):
        return readall(socket)


class HTTPWriter(object):

    def transmit_line(self, socket, line=None):
        # Transmit the line if defined
        if line:
            write(socket, line)

        # Write the newline
        write(socket, CRLF)

    def transmit_lines(self, socket, lines):
        # Transmit all lines
        for line in lines:
            self.transmit_line(socket, line)

    def transmit_artifact(self, socket, artifact):
        # Transmit all parts
        self.transmit_line(socket, artifact.header)
        self.transmit_headers(socket, artifact.headers)
        self.transmit_content(socket, artifact.content)

    def transmit_header(self, socket, name, value):
        # Write header in "key: value" format
        self.transmit_line(socket, name + SPEARATOR + WHITESPACE + value)

    def transmit_headers(self, socket, headers):
        # Loop over headers and transmit them
        for name, values in headers.items():
            for value in values:
                self.transmit_header(socket, name, value)

    def transmit_content(self, socket, content):
        # Check if content should be sent
        if content is None:
            # Send empty newline
            self.transmit_line(socket)
        else:
            # Write content-length header
            self.transmit_header(socket, CONTENT_LENGTH, INTEGER % len(content))

            # Send newline separator
            self.transmit_line(socket)

            # Send the content buffer
            write(socket, content)


class HTTPReceiver(HTTPReader):

    def receive_request(self, socket):
        # Receive artifact from parent
        artifact = self.receive_artifact(socket, content_expected=False)

        # Parse HTTP header as request header
        method, location, _ = artifact.header.split(WHITESPACE, 2)

        # Return created request
        return Request(method, location, artifact.headers, artifact.content)

    def receive_response(self, socket):
        # Receive artifact from parent
        artifact = self.receive_artifact(socket, content_expected=True)

        # Parse HTTP header as response header
        _, status, message = artifact.header.split(WHITESPACE, 2)

        # Convert status to int
        status = int(status)

        # Return created response
        return Response(status, message, artifact.headers, artifact.content)


class HTTPTransmitter(HTTPWriter):

    def transmit_request(self, socket, request):
        return self.transmit_artifact(socket, request)

    def transmit_response(self, socket, response):
        return self.transmit_artifact(socket, response)
