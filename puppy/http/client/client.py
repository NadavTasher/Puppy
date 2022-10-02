# Import python libraries
import zlib
import socket
import urllib
import collections

# Import HTTP classes
from ..interface import HTTPInterface
from ..wrappers import HTTPCompressionWrapper, HTTPConnectionStateWrapper

# Import client interface
from .interface import HTTPClientWrapper

# Import HTTP types
from ..types import Header, Request

# Import local types
from .types import History, Options

# Import URL parser
from .parser import parse


class HTTPClient(object):
    def __init__(self, options=Options(False, False)):
        # Client variables
        self._options = options

        # State variables
        self._cookies = dict()
        self._headers = list()
        self._history = list()
        self._interfaces = dict()

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

    def _update_cookies(self, headers):
        # Add cookies to cookie jar
        for name, value in headers:
            # Check if the header name is set-cookie
            if name.lower() != "set-cookie":
                continue

            # Check if semicolon exists
            if ";" in value:
                # Split by semicolon
                cookie, _ = value.split(";", 1)
            else:
                # Take as is
                cookie = value

            # Make sure '=' exists
            if "=" not in cookie:
                continue

            # Split and decode
            name, value = cookie.split("=", 1)
            name, value = urllib.unquote(name), urllib.unquote(value)

            # Update cookie jar
            self._cookies[name] = value

    def get(self, url, params={}, **kwargs):
        return self.request("GET", url, params, **kwargs)

    def post(self, location="/", parameters={}, headers=[], body=None):
        return self.request("POST", location, None, parameters, headers, body)

    def interface(self, address):
        # Check if interface already exists
        if address not in self._interfaces:
            # Create socket for address
            io = socket.socket()
            io.connect(address)

            # Create interface with socket
            self._interfaces[address] = HTTPClientWrapper(
                HTTPCompressionWrapper(HTTPConnectionStateWrapper(HTTPInterface(io)))
            )

        # Return interface for address
        return self._interfaces[address]

    def request(self, method, url, parameters={}, headers=[], body=None):
        # Parse URL using parser
        url = parse(url)

        # Find IP address of host
        address = socket.gethostbyname(url.host), url.port

        # Get interface for request by address
        interface = self.interface(address)

        # Create header list
        headers = list(headers)
        headers += self._headers

        # Append cookie header
        if self._cookies:
            headers.append(self._cookie_header)

        # Create request object
        request = Request(url.host, method, url.path, parameters, headers, body)

        # Send request using client
        interface.transmit(request)

        # Receive response using client
        response = interface.receive()

        # Update cookie jar
        self._update_cookies(response.headers)

        # Add new history item
        self._history.append(History(request, response))

        # Return response
        return response
