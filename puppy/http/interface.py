# Import gzip and io
import StringIO
import gzip

# Import typing objects
from ..typing import types

# Import required types
from .types import Header, Artifact, Options

# Operating constants
CRLF = "\r\n"
VERSION = 1.1


class Interface(object):
    def __init__(self, io, options):
        # Set internal parameters
        self._io = io
        self._options = options

    def _receive_artifact(self):
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
            connection = value if name == "connection" else connection
            content_type = value if name == "content-type" else content_type
            content_length = value if name == "content-length" else content_length
            content_encoding = value if name == "content-encoding" else content_encoding
            transfer_encoding = (
                value if name == "transfer-encoding" else transfer_encoding
            )

        # Decide which content to receive
        if content_length:
            # Receive content by length
            content = self._receive_content_by_length(content_length)
        elif transfer_encoding:
            # Make sure encoding is chunked
            assert transfer_encoding == "chunked"

            # Receive content by chunks
            content = self._receive_content_by_chunks()
        elif content_type:
            # Make sure connection is set to closed
            assert connection == "close"

            # Receive content by stream
            content = self._receive_content_by_stream()
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

    def _transmit_artifact(self, artifact):
        # Transmit HTTP header
        self._transmit_line(artifact.header)

        # Transmit all headers
        self._transmit_headers(artifact.headers)

        # Transmit content
        self._transmit_content(artifact.content)

    def _transmit_line(self, line):
        print(line)
        # Write line with CRLF
        self._io.send(line + CRLF)

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
            # Check if compression is required
            if self._options.compress:
                # Compress content using gzip
                temporary = StringIO.StringIO()
                with gzip.GzipFile(fileobj=temporary, mode="w") as compressor:
                    compressor.write(content)
                content = temporary.getvalue()

                # Transmit compression header
                self._transmit_header(Header("Content-Encoding", "gzip"))

                # Transmit supported compressions
                self._transmit_header(Header("Accept-Encoding", "gzip"))

            # Transmit content-length header
            self._transmit_header(Header("Content-Length", str(len(content))))

            # Transmit CRLF separator
            self._transmit_line(str())

            # Transmit complete contents
            self._io.send(content)
        else:
            # Transmit two CRLF separators
            self._transmit_line(str())
            self._transmit_line(str())
