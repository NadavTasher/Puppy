# Import gzip and io
import gzip
import StringIO

# Import typing objects
from ..typing import types

# Import required types
from .types import Header, Artifact, Options

# Operating constants
CRLF = "\r\n"
VERSION = 1.1
OPTIONS = Options(linger=False, compress=False)

def header(name, headers):
    # Loop over headers
    for key, value in headers:
        # If wanted name equals found name, return value
        if key.lower() == name.lower():
            return value
    
    # Default return none
    return None

class Protocol(object):
    @staticmethod
    def receive(io):
        # Receive header line
        header = Protocol.receive_line(io)

        # Receive all headers
        headers = list(Protocol.receive_headers(io))

        # Receive content (with headers)
        content = Protocol.receive_content(headers)

        # Return artifact
        return Artifact(header, headers, content)

    @staticmethod
    def receive_line(io):
        # Initialize buffer
        buffer = str()

        # Read until the CRLF exists
        while CRLF not in buffer:
            # Receive one byte into the buffer
            buffer += io.recv(1)

        # Return received buffer
        return buffer[: -len(CRLF)]

    @staticmethod
    def receive_lines(io):
        # Initialize line variable
        line = None

        # Yield lines until the line length is 0
        while line != str():
            # Yield the value if exists
            if line:
                yield line

            # Read next line
            line = Protocol.receive_line(io)

    @staticmethod
    def receive_headers(io):
        # Receive all headers
        for line in Protocol.receive_lines(io):
            # Validate header line
            if ":" not in line:
                continue

            # Split header into name and value
            name, value = line.split(":", 1)

            # Yield new header
            yield Header(name.strip(), value.strip())

    @staticmethod
    def receive_content(io, headers):
        # Find all required headers
        connection = header("Connection", headers)
        content_type = header("Content-Type", headers)
        content_length = header("Content-Length", headers)
        content_encoding = header("Content-Encoding", headers)
        transfer_encoding = header("Transfer-Encoding", headers)

        # Create temporary content variable
        content = None

        # Decide which content to receive
        if content_length:
            # Receive content by length
            content = Protocol.receive_content_by_length(io, content_length)
        elif transfer_encoding:
            # Make sure encoding is chunked
            assert transfer_encoding == "chunked"

            # Receive content by chunks
            content = Protocol.receive_content_by_chunks(io)
        elif content_type:
            # Make sure connection is set to closed
            assert connection == "close"

            # Receive content by stream
            content = Protocol.receive_content_by_stream(io)
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

    @staticmethod
    def receive_content_by_length(io, length):
        return io.recv(int(length))

    @staticmethod
    def receive_content_by_chunks(io):
        # Initialize buffer and length
        buffer = str()
        length = None

        # Read chunks until the length is 0
        while length != 0:
            # Check if length is defined
            if length:
                # Read and yield
                buffer += io.recv(length)

                # Receive line separator
                Protocol.receive_line(io)

            # Receive next length
            length = int(receive_line(io), 16)

        # Return buffer
        return buffer

    @staticmethod
    def receive_content_by_stream(io):
        # Initialize buffer and temporary
        buffer = str()
        temporary = None

        # Loop until no bytes are left
        while temporary != str():
            # Push temporary value to buffer
            if temporary:
                buffer += temporary

            # Read next byte
            temporary = io.recv(1)

        # Return buffer
        return buffer

    @staticmethod
    def transmit(io, artifact, options=OPTIONS):
        # Transmit HTTP header
        Protocol.transmit_line(io, artifact.header)

        # Transmit all headers
        Protocol.transmit_headers(io, artifact.headers)

        # Transmit content
        Protocol.transmit_content(io, artifact.content, options)

    @staticmethod
    def transmit_line(io, line=None):
        # Write given line if defined
        if line:
            io.send(line)

        # Write HTTP line separator
        io.send(CRLF)

    @staticmethod
    def transmit_header(io, header):
        # Write header with name: value format
        Protocol.transmit_line(io, "%s: %s" % (header.name, header.value))

    @staticmethod
    def transmit_headers(io, headers):
        # Loop over each header and transmit it
        for header in headers:
            Protocol.transmit_header(io, header)

    @staticmethod
    def transmit_content(io, content, options=OPTIONS):
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
                Protocol.transmit_header(io, Header("Content-Encoding", "gzip"))

                # Transmit supported compressions
                Protocol.transmit_header(io, Header("Accept-Encoding", "gzip"))

            # Transmit content-length header
            Protocol.transmit_header(io, Header("Content-Length", str(len(content))))

            # Transmit CRLF separator
            Protocol.transmit_line(io)

            # Transmit complete contents
            io.send(content)
        else:
            # Transmit two CRLF separators
            Protocol.transmit_line(io)
            Protocol.transmit_line(io)
