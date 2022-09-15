# Import gzip and io
import gzip
import StringIO

# Import required types
from .types import Interface, Wrapper, Header, Artifact, Request, Response, Options

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


class HTTPInterface(Interface):
    def __init__(self, io, options=OPTIONS):
        # Set internal variables
        self._io = io
        self._options = options

        # Initialize parent
        super(HTTPInterface, self).__init__()

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


class HTTPCompressionWrapper(Wrapper):
    _compress = False

    def receive(self):
        # Receive HTTP artifact
        artifact = self._interface.receive()

        # Check headers for encoding headers
        accept_encoding = header("Accept-Encoding", artifact.headers)
        content_encoding = header("Content-Encoding", artifact.headers)

        # Update compression state
        if not accept_encoding:
            self._compress = False
        else:
            self._compress = "gzip" in accept_encoding

        # Decompress artifact content
        if not content_encoding:
            return artifact

        # Make sure encoding is gzip
        assert content_encoding == "gzip"

        # Decompress content as gzip
        artifact = artifact._replace(content=zlib.decompress(artifact.content, 40))

        # Return modified artifact
        return artifact

    def transmit(self, artifact):
        # Check if compression is enabled
        if self._compress:
            # Fetch artifact headers and content
            headers = artifact.headers
            content = artifact.content

            # Add encoding headers
            headers.append(Header("Accept-Encoding", "gzip, deflate"))
            headers.append(Header("Content-Encoding", "gzip"))

            # Compress content using gzip
            temporary = StringIO.StringIO()
            with gzip.GzipFile(fileobj=temporary, mode="w") as compressor:
                compressor.write(content)
            content = temporary.getvalue()

            # Modify artifact with updated values
            artifact = artifact._replace(headers=headers, content=content)

        # Transmit artifact
        return self._interface.transmit(artifact)


class HTTPConnectionStateWrapper(Wrapper):
    _linger = False

    def receive(self):
        # Receive an artifact
        artifact = self._interface.receive()

        # Check connection state header
        connection = header("Connection", artifact.headers)

        # Check if connection state header was set
        if not connection:
            # Default - close connection
            self._linger = False
        else:
            # Compare header to known close value
            self._linger = connection.lower() != "close"

        # Return the artifact
        return artifact

    def transmit(self, artifact):
        # Fetch artifact headers
        headers = artifact.headers

        # Add connection headers as needed
        headers.append(Header("Connection", "keep-alive" if self._linger else "close"))

        # Modify artifact headers
        artifact = artifact._replace(headers=headers)

        # Transmit artifact as needed
        self._interface.transmit(artifact)

        # Close socket if needed
        if not self._linger:
            self.close()


class HTTPClientWrapper(Wrapper):
    def receive(self):
        # Receive artifact from parent
        artifact = self._interface.receive()

        # Parse HTTP header as response header
        _, status, message = artifact.header.split(None, 2)

        # Convert status to int
        status = int(status)

        # Return created response
        return Response(status, message, artifact.headers, artifact.content)

    def transmit(self, request, options=OPTIONS):
        # Create location string
        location = request.location

        # Check if request parameters have to be added
        if request.parameters:
            location += "?" + "&".join(
                [
                    "%s=%s" % (urllib.quote(name), urllib.quote(value))
                    for name, value in request.parameters.items()
                ]
            )

        # Create HTTP header
        header = "%s %s HTTP/%.1f" % (request.method, location, VERSION)

        # Create header list
        headers = [Header("Host", request.host)] + request.headers

        # Create an artifact with the header
        artifact = Artifact(header, headers, request.content)

        # Transmit artifact
        return self._interface.transmit(artifact)


class HTTPServerWrapper(Wrapper):
    def receive(self):
        # Receive artifact from parent
        artifact = self._interface.receive()

        # Parse HTTP header as request header
        method, location, _ = artifact.header.split(None, 2)

        # Find host header in headers
        host = header("Host", artifact.headers)

        # Initialize parameters (to be filled from query)
        parameters = dict()

        # Split location to path and query string
        if "?" in location:
            path, query = location.split("?", 1)

            # Split query by amp and parse parameters
            for parameter in query.split("&"):
                # Check if parameter contains "="
                if "=" not in parameter:
                    continue

                # Split parameter
                name, value = parameter.split("=", 1)

                # Parse as encoded parameters
                name, value = urllib.unquote(name.strip()), urllib.unquote(
                    value.strip()
                )

                # Add to dictionary
                parameters[name] = value

            # Return created request
            return Request(
                host, method, path, parameters, artifact.headers, artifact.content
            )

        # Return created request
        return Request(host, method, location, None, artifact.headers, artifact.content)

    def transmit(self, response):
        # Create HTTP header
        header = "HTTP/%.1f %d %s" % (VERSION, response.status, response.message)

        # Create an artifact with the header
        artifact = Artifact(header, response.headers, response.content)

        # Transmit artifact
        return self._interface.transmit(artifact)
