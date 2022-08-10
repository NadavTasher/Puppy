# Import python libraries
import zlib
import socket
import urllib
import collections

# Import other classes
from .classes import *
from .constants import *
from .validators import *


class HTTP(object):
    def __init__(self, io, options=DEFAULT_OPTIONS):
        # Client variables
        self._io = io
        self._options = options

        # State variables
        self._cookies = dict()
        self._headers = list()
        self._history = list()

    def post(*args, **kwargs):
        pass

    def get(*args, **kwargs):
        pass

    def request(self, method="GET", location="/", parameters={}, headers=[], body=None):
        # Create request object
        request = Request(method, location, parameters, headers, body)

        # Send request using IO
        self._io.send(
            # Render request as text
            self._render(request)
        )

        # Receive response
        response = self._receive()

        # Add new history item
        self._history.append(Artifact(request, response))

        # Add cookies to cookie jar
        pass

        # Return response
        return response

    def _render(self, request):
        # Validate the request before forming it
        assert isinstance(request, Request)

        # Copy simple variables
        method = request.method
        location = request.location

        # Figure out which headers to use
        headers = request.headers or list()

        # Add compression header
        if self._options.compress:
            headers += [REQUEST_HEADER_COMPRESS]

        # Add connection header
        if self._options.linger:
            headers += [REQUEST_HEADER_LINGER]
        else:
            headers += [REQUEST_HEADER_CLOSE]

        # Add body headers
        if request.body:
            headers += request.body.headers
            headers += [Header(HEADER_LENGTH, str(len(request.body.content)))]

        # Compile string of parameters
        parameters = (
            "?{0}".format(
                "&".join(
                    [
                        "{0}={1}".format(urllib.quote(key), urllib.quote(value))
                        for key, value in request.parameters.items()
                    ]
                )
            )
            if request.parameters
            else str()
        )

        # Render all lines of request
        lines = list()

        # Add HTTP header
        lines.append(
            "{0} {1}{2} HTTP/{3}".format(method, location, parameters, HTTP_VERSION)
        )

        # Loop over headers
        for header in headers:
            # Create header and append
            lines.append("{0}: {1}".format(header.name, header.value))

        # Add body if needed
        if request.body:
            # Add blank line
            lines.append(str())

            # Add body content
            lines.append(request.body.content)

        # Return request, join by CRLF
        return CRLF.join(lines)

    def _receive(self, request):
        # Receive HTTP header
        status, message = self._receive_header()

        # Receive request headers
        headers = list(self._receive_headers())

        # Initialize empty body
        body = None

        # Receive request body
        if request.method != "GET":
            body = self._receive_body(headers)
            body = self._decompress_body(body, headers)

        # Return new response
        return Response(status, message, headers, body)

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

    def _receive_header(self):
        # Receive one line as HTTP header
        header = self._receive_line()

        # Split header to status and message
        _, status, message = header.split(None, 2)

        # Return status and message
        return int(status), str(message)

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

    def _receive_body(self, headers):
        # Loop over headers and check them
        for header in headers:
            # Check if the header name is a content-length
            if header.name.lower() == HEADER_LENGTH.lower():
                # Parse content length and receive body
                return self._receive_length(int(header.value))

            # Check if header name is transfer-encoding
            if header.name.lower() == RESPONSE_HEADER_CHUNKED.name.lower():
                # Check if encoding is chunked
                if header.value.lower() == RESPONSE_HEADER_CHUNKED.value.lower():
                    # Receive chunked body
                    return self._receive_chunked()

        # If linger is disabled, read until there is no more data
        if not self._options.linger:
            return self._receive_stream()

    def _receive_length(self, length):
        # Initialize buffer
        buffer = str()

        # Receive n bytes
        buffer += self._io.recv(length)

        # Return buffer
        return buffer

    def _receive_chunked(self):
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

    def _receive_stream(self):
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

    def _decompress_body(self, body, headers):
        # Loop over headers and check them
        for header in headers:
            # Check if header name is content-encoding
            if header.name.lower() == RESPONSE_HEADER_COMPRESS.name.lower():
                # Check if encoding is chunked
                if header.value.lower() == RESPONSE_HEADER_COMPRESS.value.lower():
                    # Decompress body and return
                    return zlib.decompress(body, 40)

        # Return body as-is
        return body


class Browser(HTTP):
    def __init__(self, options=DEFAULT_OPTIONS):
        # Socket variables
        self._socket, self._protocol = None, socket.AF_INET
        self._source, self._destination = None, None

        # HTTP options
        self._options = options or DEFAULT_OPTIONS

        # Browser variables
        self._cookies = dict()
        self._headers = list()
        self._history = list()

    @property
    def connected(self):
        # Check if the socket is set
        return self._socket is not None

    def wrap(self, *wrappers):
        # Make sure the socket exists
        assert self._socket, "Socket does not exist"

        # Wrap the socket with all wrappers
        for wrapper in wrappers:
            self._socket = wrapper(self._socket)

    def socket(self, source=None, destination=None, protocol=None, *wrappers):
        # Make sure socket does not exist
        assert not self._socket, "Socket already exists"

        # Decide which addresses to use
        source = source or self._source
        destination = destination or self._destination

        # Make sure addresses are valid
        assert source and destination, "Addresses are not valid"

        # Decide which protocol to use
        protocol = protocol or self._protocol

        # Make sure protocol is valid
        assert protocol, "Protocol is not valid"

        # Create socket using the protocol
        stream = socket.socket(protocol, socket.SOCK_STREAM)

        # Bind and connect using addresses
        stream.bind(source)
        stream.connect(destination)

        # Wrap with all socket wrappers
        for wrapper in wrappers:
            stream = wrapper(stream)

        # Return created socket
        return stream, source, destination

    def connect(self, source=None, destination=None, secure=False, *wrappers):
        # Make sure browser is not connected already
        assert not self.connected, "Browser is already connected"

        # Connect to destination
        self._socket, self._source, self._destination = self.socket(
            source, destination, self._protocol, *[]
        )

    def request(
        self, method=None, location=None, parameters=None, body=None, headers=None
    ):
        # Create request from parameters
        request = Request(self._options)

        # Update all parameters
        request._body = body
        request._method = method
        request._headers = headers
        request._location = location
        request._parameters = parameters

        # Print created request
        print(request)


class Response(object):
    def __init__(self, options=None):
        # Response variables
        self._body = None
        self._headers = None
        self._status = None
        self._message = None

        # Browser options
        self._options = options or Browser.OPTIONS_DEFAULT

    def _receive_line(self, io):
        # Initialize buffer
        buffer = str()

        # Read until the CRLF exists
        while CRLF not in buffer:
            # Receive one byte into the buffer
            buffer += io.recv(1)

        # Return received buffer
        return buffer[: -len(CRLF)]

    def _receive_lines(self, io):
        # Initialize temporary variable
        temporary = None

        # Yield lines until the line length is 0
        while temporary != str():
            # Yield the value if exists
            if temporary:
                yield temporary

            # Read next line
            temporary = self._receive_line(io)

    def _chunk(self, io):
        # Read a line, decode the hex value
        return int(self._receive_line(io), 16)

    def _chunks(self, io):
        # Initialize temporary variable
        temporary = None

        # Yield chunks until the length is 0
        while temporary != 0:
            # Read and yield if the length exists
            if temporary:
                yield io.recv(temporary)

            # Receive next length
            temporary = self._chunk(io)

    @property
    def rendered(self):
        pass

    def receive(self, io):
        # Receive header
        _, status, message = self._receive_line(io).split(" ", 2)

        # Update status and message
        self._status = int(status.strip())
        self._message = str(message.strip())

        # Initialize header list
        headers = list()

        # Receive headers
        for header in self._receive_lines(io):
            # Validate header
            if ":" not in header:
                continue

            # Split to name and value
            name, value = header.split(":", 1)

            # Append to header list
            headers.append(Header(name.strip(), value.strip()))

        # Update headers
        self._headers = headers

        # Decide which type of body will be received
        length, stream, chunked = False, False, False

        # Loop over headers and check them
        for (name, value) in self._headers:
            pass
