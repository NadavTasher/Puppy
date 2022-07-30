# Import python libraries
import socket
import urllib
import collections

# Import other classes
from .classes import *
from .constants import *
from .validators import *

class HTTP(object):
    def __init__(self, io, options=None):
        # Client variables
        self._io = io
        self._options = options or DEFAULT_OPTIONS

        # State variables
        self._cookies = dict()
        self._headers = list()
        self._history = list()

    def post(*args, **kwargs):
        pass

    def get(*args, **kwargs):
        pass

    def request(self, method, location, parameters, headers, body):
        pass

    @validator
    def _request_validate(self, request):
        # Make sure the request is a Request
        assert isinstance(request, Request)

        # Validate each part of the request
        assert safestring(request.method) in HTTP_METHODS
        assert safestring(request.location)

    def _request_render(self, request):
        # Validate the request before forming it

class Browser(object):

    def __init__(self, options=None):
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


class Request(object):

    def __init__(self, options=None):
        # Request variables
        self._body = None
        self._method = None
        self._headers = None
        self._location = None
        self._parameters = None

        # Browser options
        self._options = options or DEFAULT_OPTIONS

    @property
    def body(self):
        # Make sure body was supplied
        if not self._body:
            # Return none - indicate no body
            return None

        # Make sure body is valid
        assert isinstance(self._body, Body)

        # Extract body value
        return self._body.content

    @property
    def headers(self):
        # Assemble complete header list
        headers = list()

        # Check if headers are set
        if self._headers:
            # Make sure headers are valid
            assert isinstance(self._headers, list)

            # Make sure all headers are valid
            for header in self._headers:
                # Append valid header
                headers.append(
                    # Validate header
                    Request._header(header)
                )

        # Add body specific headers
        if self.body:
            # Make sure headers are valid
            assert isinstance(self._body.headers, list)

            # Make sure all headers are valid
            for header in self._body.headers:
                # Append valid header
                headers.append(
                    # Validate header
                    Request._header(header)
                )

        # Add compression headers if needed
        if self._options.compress:
            # Add compression header
            headers.append(REQUEST_HEADER_COMPRESS)

        # Add connection header
        if self._options.linger:
            # Linger if option is set
            headers.append(REQUEST_HEADER_LINGER)
        else:
            # Close if option is unset
            headers.append(REQUEST_HEADER_CLOSE)

        # Add content-length header
        if self.body:
            headers.append(Header(HEADER_LENGTH, len(self.body)))

        # Return complete list of headers
        return headers

    @property
    def method(self):
        # Check if method is set
        if self._method:
            # Make sure method is valid
            assert self._method in HTTP_METHODS

        # Return the actual method
        return self._method or "GET"

    @property
    def location(self):
        # Check if location is set
        if self._location:
            # Make sure location is a valid string
            Request._string(self._location)

        # Return the actual location
        return self._location or "/"

    @property
    def parameters(self):
        # Check if parameters are set
        if not self._parameters:
            # Return empty string
            return str()

        # Make sure parameters are a dict
        assert isinstance(self._parameters, dict)

        # Convert parameters to query string
        return "?{0}".format(
            "&".join(
                [
                    # Encode as form value
                    "{0}={1}".format(
                        # Encode form key
                        urllib.quote(key),
                        # Encode form value
                        urllib.quote(value),
                    )
                    # All values in the dictionary
                    for key, value in self._parameters.items()
                ]
            )
        )

    @property
    def rendered(self):
        # Assemble complete request
        request = list()

        # Add HTTP header
        request.append(
            "{0} {1}{2} HTTP/{3}".format(
                # Request method
                self.method,
                # Location (URI)
                self.location,
                # Query parameters
                self.parameters,
                # HTTP version
                Request.HTTP_VERSION,
            )
        )

        # Append all headers
        for (name, value) in self.headers:
            # Create header and append
            request.append(
                "{0}: {1}".format(
                    # Header name
                    name,
                    # Header value
                    value,
                )
            )

        # Append body if needed
        if self.body:
            # Append empty string to request
            request.append(str())

            # Append request body content
            request.append(self.body)

        # Format request to string
        return "\r\n".join(request)

    def transmit(self, io):
        io.send(self.rendered)


class Response(object):
    def __init__(self, options=None):
        # Response variables
        self._body = None
        self._headers = None
        self._status = None
        self._message = None

        # Browser options
        self._options = options or Browser.OPTIONS_DEFAULT

    def _line(self, io):
        # Initialize buffer
        buffer = str()

        # Read until the CRLF exists
        while CRLF not in buffer:
            # Receive one byte into the buffer
            buffer += io.recv(1)

        # Return received buffer
        return buffer[: -len(CRLF)]

    def _lines(self, io):
        # Initialize temporary variable
        temporary = None

        # Yield lines until the line length is 0
        while temporary != str():
            # Yield the value if exists
            if temporary:
                yield temporary

            # Read next line
            temporary = self._line(io)

    def _chunk(self, io):
        # Read a line, decode the hex value
        return int(self._line(io), 16)

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
        _, status, message = self._line(io).split(" ", 2)

        # Update status and message
        self._status = int(status.strip())
        self._message = str(message.strip())

        # Initialize header list
        headers = list()

        # Receive headers
        for header in self._lines(io):
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