from puppy.socket.wrapper import SocketReader, SocketWriter
from puppy.http.types.headers import Headers
from puppy.http.types.request import Request
from puppy.http.types.response import Response
from puppy.http.types.artifact import Received
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


class HTTPReader(SocketReader):

    def receive_artifact(self, content_expected=True):
        # Receive all artifact components
        header = self.readline()
        headers = self.receive_headers()
        content = self.receive_content(headers, content_expected)

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

            # Append new header
            if name not in headers:
                headers[name] = value
            else:
                headers[name] += value

        # Return the headers object
        return headers

    def receive_content(self, headers, content_expected=True):
        # If a length is defined, fetch by length
        if CONTENT_LENGTH in headers:
            # Fetch content-length header
            (content_length,) = headers.pop(CONTENT_LENGTH)

            # Read content by known length
            return self.receive_content_by_length(int(content_length))

        # If encoding is defined, fetch by chunks
        if TRANSFER_ENCODING in headers:
            # Fetch transfer-encoding header
            (transfer_encoding,) = headers.pop(TRANSFER_ENCODING)

            # Make sure the encoding is supported
            assert transfer_encoding.lower() == CHUNKED

            # Receive by chunks
            return self.receive_content_by_chunks()

        # Make sure content-type is defined
        if CONTENT_TYPE not in headers:
            return

        # Make sure content is expected
        if not content_expected:
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

    def readline(self, separator=CRLF):
        return super(HTTPReader, self).readline(separator)

    def readlines(self, separator=CRLF):
        return super(HTTPReader, self).readlines(separator)


class HTTPWriter(SocketWriter):

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
        for name, values in headers.items():
            for value in values:
                self.transmit_header(name, value)

    def transmit_content(self, content):
        # Check if content should be sent
        if content is None:
            # Send empty newline
            self.writeline()
        else:
            # Write content-length header
            self.transmit_header(CONTENT_LENGTH, INTEGER % len(content))

            # Send newline separator
            self.writeline()

            # Send the content buffer
            self.sendall(content)

    def writeline(self, line=bytes(), separator=CRLF):
        return super(HTTPWriter, self).writeline(line, separator)

    def writelines(self, lines, separator=CRLF):
        return super(HTTPWriter, self).writelines(lines, separator)


class HTTPReceiver(HTTPReader):

    def receive_request(self):
        # Receive artifact from parent
        artifact = self.receive_artifact(content_expected=False)

        # Parse HTTP header as request header
        method, location, _ = artifact.header.split(WHITESPACE, 2)

        # Return created request
        return Request(method, location, artifact.headers, artifact.content)

    def receive_response(self):
        # Receive artifact from parent
        artifact = self.receive_artifact(content_expected=True)

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
