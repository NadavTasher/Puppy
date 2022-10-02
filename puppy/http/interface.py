# Import required types
from .types import Header, Artifact

# Operating constants
CRLF = "\r\n"
VERSION = 1.1


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

    def _receive_content_by_length(self, length):
        return self._io.recv(int(length))

    def _receive_content_by_chunks(self):
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

        # Return buffer
        return buffer

    def _receive_content_by_stream(self):
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
