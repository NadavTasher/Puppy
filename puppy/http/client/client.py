# Import python libraries
import zlib
import socket
import urllib
import collections

from puppy.http.types import Header, Request
from puppy.http.interface import *
from puppy.http.client.types import History, Options
from puppy.http.client.parser import parse
from puppy.http.client.constants import *


class HTTPClientInterface(
    HTTPReceiver,
    HTTPTransmitter,
    HTTPGzipReceiverMixIn,
    HTTPGzipTransmitterMixIn,
    HTTPConnectionStateReceiverMixIn,
    HTTPConnectionStateTransmitterMixIn,
):
    pass


class HTTPClient(object):
    def __init__(self, implementation=HTTPClientInterface):
        # Client variables
        self.implementation = implementation

        # State variables
        self.cookies = dict()
        self.headers = list()
        self.history = list()
        self.interfaces = dict()

    def _update_cookies(self, headers):
        # Add cookies to cookie jar
        for header in headers:
            # Check if the header name is set-cookie
            if not compare(header.name, SET_COOKIE):
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
            self.cookies[name] = value

    def get(self, url, params={}, **kwargs):
        return self.request("GET", url, params, **kwargs)

    def post(self, location="/", parameters={}, headers=[], body=None):
        return self.request("POST", location, None, parameters, headers, body)

    def socket(self, address):
        # Create socket for address
        io = socket.socket()
        io.connect(address)

        # Return created socket
        return io

    def interface(self, address):
        # Check if interface already exists
        if address not in self.interfaces:
            # Create client interface
            self.interfaces[address] = self.implementation(self.socket(address))

        # Return interface for address
        return self.interfaces[address]

    def request(self, method, url, parameters={}, headers=[], body=None):
        # Parse URL using parser
        url = parse(url)

        # Find IP address of host
        address = socket.gethostbyname(url.host), url.port

        # Get interface for request by address
        interface = self.interface(address)

        # Create header list
        headers = list(headers)
        headers += self.headers

        # Append cookie header
        if self.cookies:
            headers.append(
                Header(
                    COOKIE,
                    "; ".join(
                        [
                            # Format as name=value
                            "%s=%s" % (urllib.quote(name), urllib.quote(value))
                            # For each cookie in the jar
                            for name, value in self.cookies.items()
                        ]
                    ),
                )
            )

        # Create request object
        request = Request(url.host, method, url.path, parameters, headers, body)

        # Send request using client
        interface.transmit_request(request)

        # Receive response using client
        response = interface.receive_response()

        # Update cookie jar
        self._update_cookies(response.headers)

        # Add new history item
        self.history.append(History(request, response))

        # Return response
        return response
