# Import python libraries
import zlib
import socket
import urllib
import collections

# Import other classes
from .classes import *
from .constants import *


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
            # Format form parameters
            "?{0}".format(
                "&".join(
                    [
                        "{0}={1}".format(urllib.quote(key), urllib.quote(value))
                        for key, value in request.parameters.items()
                    ]
                )
            )
            # If parameters exist
            if request.parameters
            # Or just use an empty string
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

    def _receive(self):
        # Receive HTTP header
        status, message = self._receive_header()

        # Receive request headers
        headers = list(self._receive_headers())

        # Receive request body
        body = self._receive_body(headers)
        body = self._decompress_body(body, headers)

        # Return new response
        return Response(status, message, headers, body)

    def _receive_header(self):
        # Receive one line as HTTP header
        header = self._receive_line()

        # Split header to status and message
        _, status, message = header.split(None, 2)

        # Return status and message
        return int(status), str(message)

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