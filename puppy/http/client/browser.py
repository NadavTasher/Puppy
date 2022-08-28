# Import python libraries
import zlib
import socket
import urllib
import collections

# Import other classes
from ..types import Header, Request, History
from ..client import Client
from ..constants import DEFAULT_OPTIONS


class Browser(object):
    def __init__(self, io, options=DEFAULT_OPTIONS):
        # Client variables
        self._io = io
        
        self._options = options

        # Create client object
        self._client = Client(io, options)

        # State variables
        self._cookies = dict()
        self._headers = list()
        self._history = list()

    @property
    def _cookie_header(self):
        return Header(
            "Cookie",
            "; ".join(
                [
                    # Format as name=value
                    "%s=%s" % (urllib.quote(name), urllib.quote(value))
                    # For each cookie in the jar
                    for name, value in self._cookies.items()
                ]
            ),
        )

    @property
    def _host_header(self):
        return Header(
            "Host",

        )

    def _update_cookies(self, headers):
        # Add cookies to cookie jar
        for header in headers:
            # Check if the header name is set-cookie
            if header.name.lower() != "set-cookie":
                continue

            # Check if semicolon exists
            if ";" in header.value:
                # Split by semicolon
                cookie, _ = header.value.split(";", 1)
            else:
                # Take as is
                cookie = header.value

            # Make sure '=' exists
            if "=" not in cookie:
                continue

            # Split and decode
            name, value = cookie.split("=", 1)
            name, value = urllib.unquote(name), urllib.unquote(value)

            # Update cookie jar
            self._cookies[name] = value

    def get(self, location="/", parameters={}, headers=[]):
        return self.request("GET", location, parameters, headers)

    def post(self, location="/", parameters={}, headers=[], body=None):
        return self.request("POST", location, parameters, headers, body)

    def request(self, method="GET", location="/", parameters={}, headers=[], body=None):
        # Create header list
        headers = list(headers)
        headers += self._headers

        # Append host header
        headers.append(self._host_header)

        # Append cookie header
        if self._cookies:
            headers.append(self._cookie_header)

        # Create request object
        request = Request(method, location, parameters, headers, body)

        # Send request using client
        self._client.transmit(request)

        # Receive response using client
        response = self._client.receive()

        # Update cookie jar
        self._update_cookies(response.headers)

        # Add new history item
        self._history.append(History(request, response))

        # Return response
        return response


# class Browser(HTTP):
#     def __init__(self, options=DEFAULT_OPTIONS):
#         # Socket variables
#         self._socket, self._protocol = None, socket.AF_INET
#         self._source, self._destination = None, None

#         # HTTP options
#         self._options = options or DEFAULT_OPTIONS

#         # Browser variables
#         self._cookies = dict()
#         self._headers = list()
#         self._history = list()

#     @property
#     def connected(self):
#         # Check if the socket is set
#         return self._socket is not None

#     def wrap(self, *wrappers):
#         # Make sure the socket exists
#         assert self._socket, "Socket does not exist"

#         # Wrap the socket with all wrappers
#         for wrapper in wrappers:
#             self._socket = wrapper(self._socket)

#     def socket(self, source=None, destination=None, protocol=None, *wrappers):
#         # Make sure socket does not exist
#         assert not self._socket, "Socket already exists"

#         # Decide which addresses to use
#         source = source or self._source
#         destination = destination or self._destination

#         # Make sure addresses are valid
#         assert source and destination, "Addresses are not valid"

#         # Decide which protocol to use
#         protocol = protocol or self._protocol

#         # Make sure protocol is valid
#         assert protocol, "Protocol is not valid"

#         # Create socket using the protocol
#         stream = socket.socket(protocol, socket.SOCK_STREAM)

#         # Bind and connect using addresses
#         stream.bind(source)
#         stream.connect(destination)

#         # Wrap with all socket wrappers
#         for wrapper in wrappers:
#             stream = wrapper(stream)

#         # Return created socket
#         return stream, source, destination

#     def connect(self, source=None, destination=None, secure=False, *wrappers):
#         # Make sure browser is not connected already
#         assert not self.connected, "Browser is already connected"

#         # Connect to destination
#         self._socket, self._source, self._destination = self.socket(
#             source, destination, self._protocol, *[]
#         )

#     def request(
#         self, method=None, location=None, parameters=None, body=None, headers=None
#     ):
#         # Create request from parameters
#         request = Request(self._options)

#         # Update all parameters
#         request._body = body
#         request._method = method
#         request._headers = headers
#         request._location = location
#         request._parameters = parameters

#         # Print created request
#         print(request)
