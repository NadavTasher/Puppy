# Import typing objects
from ..typing import types

# Import required types
from .types import Header, Artifact, Options


class Interface(object):
    @types(io=Any, options=Options)
    def __init__(self, io, options):
        # Set internal parameters
        self._io = io
        self._options = options

    def receive_line(self):
        # Initialize buffer
        buffer = str()

        # Read until the CRLF exists
        while CRLF not in buffer:
            # Receive one byte into the buffer
            buffer += self._io.recv(1)

        # Return received buffer
        return buffer[: -len(CRLF)]

    def receive_lines(self):
        # Initialize line variable
        line = None

        # Yield lines until the line length is 0
        while line != str():
            # Yield the value if exists
            if line:
                yield line

            # Read next line
            line = self.receive_line()

    def receive_headers(self):
        # Receive all headers
        for line in self.receive_lines():
            # Validate header line
            if ":" not in line:
                continue

            # Split header into name and value
            name, value = line.split(":", 1)

            # Yield new header
            yield Header(name.strip(), value.strip())

    def receive_content(self, headers):
        # Create temporary variables
        content = None
        connection = None
        content_type = None
        content_length = None
        content_encoding = None
        transfer_encoding = None

        # Loop over headers and check them
        for name, value in headers:
            # Convert name and value to lowercase
            name, value = name.lower(), value.lower()

            # Check header names and update
            content_type = value if name == "content-type" else content_type
            content_length = value if name == "content-length" else content_length
            content_encoding = value if name == "content-encoding" else content_encoding
            transfer_encoding = value if name == "transfer-encoding" else transfer_encoding

        # Decide which content to receive
        if content_length:
            # Receive content by length
            content = self.receive_by_length(content_length)
        elif transfer_encoding:
            # Make sure encoding is chunked
            assert transfer_encoding == "chunked"

            # Receive content by chunks
            content = self.receive_by_chunks()
        elif connection == "close" and content_type:
            # Receive content by stream
            content = self.receive_by_stream()
        else:
            # No content to be received
            return None

        # Check if compression was provided
        if content_encoding:
            # Make sure encoding is gzip
            assert content_encoding == "gzip"

            # Decompress content as gzip
            content = zlib.decompress(content, 40)

        # Return content string
        return content

    def receive_by_length(self, length):
        return self._io.recv(int(length))

    def receive_by_chunks(self):
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
                self.receive_line()

            # Receive next length
            length = int(self.receive_line(), 16)

        # Return buffer
        return buffer

    def receive_by_stream(self):
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

    def receive(self):
        # Receive header line
        header = self.receive_line()
        
        # Receive all headers
        headers = list(self.receive_headers())

        # Receive content (with headers)
        content = self.receive_content(headers)

        # Return artifact
        return Artifact(header, headers, content)

    def transmit_line(self, line):
        # Write line with CRLF
        self._io.send(line + CRLF)

    def transmit_header(self, header):
        # Write header with name: value format
        self.transmit_line("%s: %s" % (header.name, header.value))

    def transmit_headers(self, headers):
        # Loop over each header and transmit it
        for header in headers:
            self.transmit_header(header)

    def transmit_content(self, content, compress=False):
        # Check if compression is required
        if compress:
            # Compress content using gzip
            content = content

            # Transmit compression header
            self.transmit_header(Header("Content-Encoding", "gzip"))

        # Transmit content-length header
        self.transmit_header(Header("Content-Length", str(len(content))))

        # Transmit CRLF separator
        self.transmit_line(str())

        # Transmit complete contents
        self._io.send(content)

    def transmit(self, artifact):
        # Transmit HTTP header
        self.transmit_line(artifact.header)

        # Transmit all headers
        self.transmit_headers(artifact.headers)

        # Transmit content
        self.transmit_content(artifact.content, self._options.compress)
