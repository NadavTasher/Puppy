import socket  # NOQA
import urllib  # NOQA

from puppy.http.http import HTTP  # NOQA
from puppy.http.types import Request, Headers  # NOQA
from puppy.http.utilities import urlsplit  # NOQA
from puppy.http.client.constants import COOKIE, SET_COOKIE, SCHEMA_HTTP, SCHEMA_MAPPING  # NOQA


class HTTPClient(object):
    def __init__(self, implementation=HTTP):
        # Client variables
        self.implementation = implementation

        # State variables
        self.cookies = dict()
        self.headers = list()
        self.history = list()
        self.interfaces = dict()

    def _update_request(self, request):
        # Set cookies header
        if self.cookies:
            request.headers.update(
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

        # Return the request
        return request

    def _update_response(self, response):
        # Update cookie jar with response headers
        for header in response.headers.pop(SET_COOKIE):
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

        # Return the response
        return response

    def get(self, url, *args, **kwargs):
        return self.request(b"GET", url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self.request(b"POST", url, *args, **kwargs)

    def interface(self, address):
        # Check if interface already exists
        if address not in self.interfaces:
            # Connect to socket
            connection = socket.socket()
            connection.connect(address)

            # Create client interface
            self.interfaces[address] = self.implementation(connection)

        # Return interface for address
        return self.interfaces[address]

    def request(self, method, url, headers=[], body=None):
        # Parse URL using parser
        schema, host, port, path = urlsplit(url)

        # Make sure port is defined
        schema = schema or SCHEMA_HTTP
        port = port or SCHEMA_MAPPING[schema]

        # Find IP address of host
        address = socket.gethostbyname(host), port

        # Get interface for request by address and update host
        interface = self.interface(address)
        interface.host = host

        # Create request object
        request = Request(method, path, Headers(headers), body)

        # Update the request
        request = self._update_request(request)

        # Send request using client
        interface.transmit_request(request)

        # Receive response using client
        response = interface.receive_response()

        # Update the response
        response = self._update_response(response)

        # Add new history item
        self.history.append((request, response))

        # Return response
        return response
