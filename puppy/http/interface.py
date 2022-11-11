# Import socket utilities
from puppy.socket.wrapper import SocketWrapper

# Import required types
from puppy.http.types import Header, Artifact

# Operating constants
CRLF = "\r\n"
VERSION = 1.1
SEPARATOR = ":"

# Header constants
CONNECTION = "Connection"
CONTENT_TYPE = "Content-Type"
CONTENT_LENGTH = "Content-Length"
CONTENT_ENCODING = "Content-Encoding"
TRANSFER_ENCODING = "Transfer-Encoding"

# Value constants
GZIP = "gzip"
CHUNKED = "chunked"


class SocketReader(SocketWrapper):
    def receive_line(self):
        # Create a reading buffer
        buffer = bytearray()

        # Loop until CRLF in buffer
        while CRLF not in buffer:
            buffer += self.recv(1)

        # Return the buffer without the CRLF
        return buffer[: -len(CRLF)]

    def receive_lines(self):
        # Read first line
        line = self.receive_line()

        # Loop while line is not empty
        while line:
            # Yield the received line
            yield line

            # Read the next line
            line = self.receive_line()


class SocketWriter(SocketWrapper):
    def transmit_line(self, line=None):
        # Write line if exists
        if line:
            self.send(line)

        # Write line separator
        self.send(CRLF)

    def transmit_lines(self, lines=[]):
        # Loop over lines and send them
        for line in lines:
            self.transmit_line(line)


class HTTPReader(SocketReader):
    def receive_artifact(self):
        # Receive all artifact components
        header = self.receive_line()
        headers = list(self.receive_headers())
        content = self.receive_content(headers)

        # Return created artifact
        return Artifact(header, headers, content)

    def receive_headers(self):
        for line in self.receive_lines():
            # Validate header structure
            if SEPARATOR not in line:
                continue

            # Split header line and create object
            name, value = line.split(SEPARATOR, 1)

            # Yield new header
            yield Header(name.strip(), value.strip())

    def receive_content(self, headers):
        # Fetch all of the required headers
        content_type = fetch_header(CONTENT_TYPE, headers)
        content_length = fetch_header(CONTENT_LENGTH, headers)
        transfer_encoding = fetch_header(TRANSFER_ENCODING, haeders)

        # If a length is defined, fetch by length
        if content_length:
            return self.receive_content_by_length(int(content_length.decode()))

        # If encoding is defined, fetch by chunks
        if transfer_encoding:
            # Make sure the encoding is supported
            assert compare(transfer_encoding, CHUNKED)

            # Receive by chunks
            return self.receive_content_by_chunks()

        # If a content type is defined, receive by stream
        if content_type:
            return self.receive_content_by_stream()

    def receive_content_by_length(self, length):
        return self.recv(length)

    def receive_content_by_chunks(self):
        # Initialize buffer and length
        buffer = str()
        length = None

        # Read chunks until the length is 0
        while length != 0:
            # Check if length is defined
            if length:
                # Read and yield
                buffer += self._io.recv(length)

                # Receive line separator
                self._receive_line()

            # Receive next length
            length = int(self._receive_line(), 16)

        # Read empty line
        self._receive_line()

        # Return buffer
        return buffer

    def receive_content_by_stream(self, limit=1024 * 1024):
        # Initialize buffer and temporary
        buffer = str()
        temporary = None

        # Loop until no bytes are left
        while temporary != str():
            # Push temporary value to buffer
            if temporary:
                buffer += temporary

            # Read next byte
            temporary = self._io.recv(1)

        # Return buffer
        return buffer


class HTTPInterface(object):
    def __init__(self, io):
        # Set internal variables
        self._io = io

    def receive(self):
        # Receive header line
        header = self._receive_line()

        # Receive all headers
        headers = list(self._receive_headers())

        # Receive content (with headers)
        content = self._receive_content(headers)

        # Return artifact
        return Artifact(header, headers, content)

    def _receive_line(self):
        # Initialize buffer
        buffer = str()

        # Read until the CRLF exists
        while CRLF not in buffer:
            # Receive one byte into the buffer
            buffer += self._io.recv(1)
            # TODO: fix bug

        # Return received buffer
        return buffer[: -len(CRLF)]

    def _receive_lines(self):
        # Initialize line variable
        line = None

        # Yield lines until the line length is 0
        while line != str():
            # Yield the value if exists
            if line:
                yield line

            # Read next line
            line = self._receive_line()

    def _receive_headers(self):
        # Receive all headers
        for line in self._receive_lines():
            # Validate header line
            if ":" not in line:
                continue

            # Split header into name and value
            name, value = line.split(":", 1)

            # Yield new header
            yield Header(name.strip(), value.strip())

    def _receive_content(self, headers):
        # Set the content flag ahead of time
        content = False

        # Loop over all headers and set values
        for key, value in headers:
            # Change key to lower case
            key = key.lower()

            # Check if the content-length header is set
            if key == "content-length":
                return self._receive_content_by_length(value)

            # Check if the transfer-encoding header is set
            if key == "transfer-encoding":
                return self._receive_content_by_chunks()

            # Check if the content-type header is set
            if key == "content-type":
                content = True

        # Check if should receive body
        if content:
            return self._receive_content_by_stream()

        # Return none by default
        return None

    def transmit(self, artifact):
        # Transmit HTTP header
        self._transmit_line(artifact.header)

        # Transmit all headers
        self._transmit_headers(artifact.headers)

        # Transmit content
        self._transmit_content(artifact.content)

    def _transmit_line(self, line=None):
        # Write given line if defined
        if line:
            self._io.send(line)

        # Write HTTP line separator
        self._io.send(CRLF)

    def _transmit_header(self, header):
        # Write header with name: value format
        self._transmit_line("%s: %s" % (header.name, header.value))

    def _transmit_headers(self, headers):
        # Loop over each header and transmit it
        for header in headers:
            self._transmit_header(header)

    def _transmit_content(self, content):
        # Check if content is even defined
        if content:
            # Transmit content-length header
            self._transmit_header(Header("Content-Length", str(len(content))))

            # Transmit CRLF separator
            self._transmit_line()

            # Transmit complete contents
            self._io.send(content)
        else:
            # Transmit two CRLF separators
            self._transmit_line()
            self._transmit_line()

    def close(self):
        # Close socket!
        self._io.close()
