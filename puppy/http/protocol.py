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


class HTTPReceiver(object):

    def _receive(self, socket, length):
        # Receive bytes by length
        return socket.recv(length)

    def _receive_all(self, socket, chunk=4096):
        # Initialize reading buffer
        buffer = bytes()

        # Receive the first chunk
        temporary = self._receive(socket, chunk)

        # Loop until buffer is full
        while temporary:
            # Append to buffer
            buffer += temporary

            # Receive the next chunk
            temporary = self._receive(socket, chunk)

        # Return the buffer
        return buffer

    def _receive_exact(self, socket, length, chunk=4096):
        # Initialize reading buffer
        buffer = bytes()

        # Make sure buffer is exactly the right size
        while len(buffer) < length:
            # Receive a chunk
            temporary = self._receive(socket, min(length - len(buffer), chunk))

            # Make sure data was read
            if not temporary:
                raise IOError("No more data to read")

            # Append the chunk to the buffer
            buffer += temporary

        # Return the buffer
        return buffer

    def _receive_until(self, socket, sequence):
        # Create a reading buffer
        buffer = bytes()

        # Loop until needle in buffer
        while sequence not in buffer:
            buffer += self._receive_exact(socket, 1)

        # Strip the buffer of the separator
        return buffer

    def _receive_line(self, socket):
        # Receive until CRLF and trim CRLF
        return self._receive_until(socket, CRLF)[:-len(CRLF)]

    def _receive_lines(self, socket):
        # Initialize first line
        line = self._receive_line(socket)

        # Loop until no lines are left
        while line:
            # Yield the line
            yield line

            # Read the next line
            line = self._receive_line(socket)

    def _receive_artifact(self, socket, content_expected=True):
        # Receive all artifact components
        header = self._receive_line(socket)
        headers = self._receive_headers(socket)
        content = self._receive_content(socket, headers, content_expected)

        # Return created artifact
        return Received(header, headers, content)

    def _receive_headers(self, socket):
        # Create headers object
        headers = Headers()

        # Loop over all lines
        for line in self._receive_lines(socket):
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

    def _receive_content(self, socket, headers, content_expected=True):
        # If a length is defined, fetch by length
        if CONTENT_LENGTH in headers:
            # Fetch content-length header
            (content_length,) = headers.pop(CONTENT_LENGTH)

            # Read content by known length
            return self._receive_content_by_length(socket, int(content_length))

        # If encoding is defined, fetch by chunks
        if TRANSFER_ENCODING in headers:
            # Fetch transfer-encoding header
            (transfer_encoding,) = headers.pop(TRANSFER_ENCODING)

            # Make sure the encoding is supported
            assert transfer_encoding.lower() == CHUNKED

            # Receive content by chunks
            return self._receive_content_by_chunks(socket)

        # Make sure content-type is defined
        if CONTENT_TYPE not in headers:
            return

        # Make sure content is expected
        if not content_expected:
            return

        # Receive content until socket is closed
        return self._receive_content_by_stream(socket)

    def _receive_content_by_chunks(self, socket):
        # Receive by chunks
        buffer = bytes()
        length = int(self._receive_line(socket), 16)

        # Loop until no more chunks
        while length:
            # Receive the chunk
            buffer += read(socket, length)

            # Read an empty line
            self._receive_line(socket)

            # Receive the next length
            length = int(self._receive_line(socket), 16)

        # Receive the last line
        self._receive_line(socket)

        # Return the buffer
        return buffer

    def _receive_content_by_length(self, socket, length):
        # Read content by known length
        return self._receive_exact(socket, length)

    def _receive_content_by_stream(self, socket):
        # Read content until closed
        return self._receive_all(socket)

    def receive_request(self, socket):
        # Receive artifact from parent
        artifact = self._receive_artifact(socket, content_expected=False)

        # Parse HTTP header as request header
        method, location, _ = artifact.header.split(WHITESPACE, 2)

        # Return created request
        return Request(method, location, artifact.headers, artifact.content)

    def receive_response(self, socket):
        # Receive artifact from parent
        artifact = self._receive_artifact(socket, content_expected=True)

        # Parse HTTP header as response header
        _, status, message = artifact.header.split(WHITESPACE, 2)

        # Convert status to int
        status = int(status)

        # Return created response
        return Response(status, message, artifact.headers, artifact.content)


class HTTPTransmitter(object):

    def _transmit(self, socket, buffer):
        # Send all of the data
        while buffer:
            # Send as many bytes as possible
            offset = socket.send(buffer)

            # Split the data at the offset
            buffer = buffer[offset:]

    def _transmit_line(self, socket, line=bytes()):
        # Transmit the line if defined
        self._transmit(socket, line + CRLF)

    def _transmit_lines(self, socket, lines):
        # Transmit all lines
        for line in lines:
            self._transmit_line(socket, line)

    def _transmit_artifact(self, socket, artifact):
        # Transmit all parts
        self._transmit_line(socket, artifact.header)
        self._transmit_headers(socket, artifact.headers)
        self._transmit_content(socket, artifact.content)

    def _transmit_header(self, socket, name, value):
        # Write header in "key: value" format
        self._transmit_line(socket, name + SPEARATOR + WHITESPACE + value)

    def _transmit_headers(self, socket, headers):
        # Loop over headers and transmit them
        for name, values in headers.items():
            for value in values:
                self._transmit_header(socket, name, value)

    def _transmit_content(self, socket, content):
        # Check if content should be sent
        if content is None:
            # Send empty newline
            self._transmit_line(socket)
        else:
            # Write content-length header
            self._transmit_header(socket, CONTENT_LENGTH, INTEGER % len(content))

            # Send newline separator
            self._transmit_line(socket)

            # Send the content buffer
            self._transmit(socket, content)

    def transmit_request(self, socket, request):
        return self._transmit_artifact(socket, request)

    def transmit_response(self, socket, response):
        return self._transmit_artifact(socket, response)
