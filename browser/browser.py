# Import python libraries
import socket
import urllib
import collections

# Import other classes
from .body import Body

# Create options class
Options = collections.namedtuple("Options", ["linger", "compress"])


class Browser(object):

    # Initialize constants
    OPTIONS_DEFAULT = Options(linger=False, compress=False)

    def __init__(self, options=None):
        # Socket variables
        self._socket, self._protocol = None, socket.AF_INET
        self._source, self._destination = None, None

        # HTTP options
        self._options = options or Browser.OPTIONS_DEFAULT

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

    def _receive_chunked_body(self):
        pass

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

    # Initialize constants
    HTTP_VERSION = 1.1
    HTTP_METHODS = ["GET", "POST"]

    def __init__(self, options=None):
        # Request variables
        self._body = None
        self._method = None
        self._headers = None
        self._location = None
        self._parameters = None

        # Browser options
        self._options = options or Browser.OPTIONS_DEFAULT

    @staticmethod
    def _string(string):
        # Make sure the given string is a string
        assert isinstance(string, str)

        # Make sure the string is of larger length then 0
        assert len(string) > 0

        # Make sure the string is safe
        assert all(map(lambda char: ord(char) >= 0x20, string))

        # Return variable
        return string

    @staticmethod
    def _header(header):
        # Make sure the given header is a list
        assert isinstance(header, (list, tuple))

        # Make sure the list is of length 2
        assert len(header) == 2

        # Make sure all the values in the list are safe strings
        for entry in header:
            # Make sure the variable is set and safe
            Request._string(entry)

        # Return header
        return header

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
            headers.append(
				("Accept-Encoding", "gzip")
			)

        # Add connection header
        headers.append(
            ("Connection", "Keep-Alive" if self._options.linger else "Close")
        )

        # Add content-length header
        if self.body:
            headers.append(
				("Content-Length", len(self.body))
			)

        # Return complete list of headers
        return headers

    @property
    def method(self):
        # Check if method is set
        if self._method:
            # Make sure method is valid
            assert self._method in Request.HTTP_METHODS

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

    def __str__(self):
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


class Response(object):
    pass
