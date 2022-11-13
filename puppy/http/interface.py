# Import socket utilities
from puppy.socket.io import SocketReader, SocketWriter

# Import required types
from puppy.http.types import Header, Artifact
from puppy.http.constants import *
from puppy.http.utilities import fetch_header

# Operating constants
VERSION = 1.1


class HTTPReader(SocketReader):
    def receive_artifact(self):
        # Receive all artifact components
        header = self.readline()
        headers = list(self.receive_headers())
        content = self.receive_content(headers)

        # Return created artifact
        return Artifact(header, headers, content)

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
            headers.add_header(name.strip(), value.strip())

        # Return the headers object
        return headers

    def receive_content(self, headers):
        # Fetch all of the required headers
        (content_length,) = headers.get_header(CONTENT_LENGTH)
        (transfer_encoding,) = headers.get_header(TRANSFER_ENCODING)

        # If a length is defined, fetch by length
        if content_length:
            return self.receive_content_by_length(int(content_length.decode()))

        # If encoding is defined, fetch by chunks
        if transfer_encoding:
            # Make sure the encoding is supported
            assert transfer_encoding.lower() == CHUNKED

            # Receive by chunks
            return self.receive_content_by_chunks()

        # If a content type is defined, receive by stream
        if headers.has_header(CONTENT_TYPE):
            return self.receive_content_by_stream()

    def receive_content_by_length(self, length):
        return self.recv(length)

    def receive_content_by_chunks(self):
        # Initialize buffer and length
        length = None
        buffer = bytearray()

        # Loop until length is 0
        while length != 0:
            # Receive the next chunk's length
            length = int(self.readline(), 16)

            # Yield the line's length
            buffer += self.recv(length)

            # Read separator line
            self.readline()

        # Return created buffer
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


class HTTPWriter(SocketWriter):
    def transmit_artifact(self, artifact):
        # Transmit all parts
        self.writeline(artifact.header)
        self.transmit_headers(artifact.headers)
        self.transmit_content(artifact.content)

    def transmit_header(self, header):
        # Write header in "key: value" format
        self.writeline("%s: %s" % header)

    def transmit_headers(self, headers):
        # Loop over headers and transmit them
        for header in headers:
            self.transmit_header(header)

    def transmit_content(self, content):
        # If content is defined, write a content-length header
        if content:
            self.transmit_header(Header(CONTENT_LENGTH, str(len(content))))

        # Write HTTP separator (empty line)
        self.writeline()

        # If content is defined, send it
        if content:
            # Send the content as is
            self.send(content)
        else:
            # Send empty content
            self.writeline()


class HTTPReceiver(HTTPReader):
    def receive_request(self):
        # Receive artifact from parent
        artifact = self.receive_artifact()

        # Parse HTTP header as request header
        method, location, _ = artifact.header.split(None, 2)

        # Find host header value
        host = fetch_header(HOST, artifact.headers)

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
                name = urllib.unquote(name.strip())
                value = urllib.unquote(value.strip())

                # Add to dictionary
                parameters[name] = value

            # Return created request
            return Request(
                host, method, path, parameters, artifact.headers, artifact.content
            )

        # Return created request
        return Request(host, method, location, None, artifact.headers, artifact.content)

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
        headers = request.headers

        # Insert host header if needed
        if request.host:
            headers.insert(0, Header("Host", request.host))

        # Transmit artifact
        return self.transmit_artifact(Artifact(header, headers, request.content))

    def transmit_response(self, response):
        # Create HTTP header
        header = "HTTP/%.1f %d %s" % (VERSION, response.status, response.message)

        # Transmit artifact
        return self.transmit_artifact(
            Artifact(header, response.headers, response.content)
        )
