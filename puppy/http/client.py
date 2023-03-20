import ssl
import socket

from puppy.http.url import urlsplit
from puppy.http.http import HTTP
from puppy.http.types.headers import Headers
from puppy.http.types.request import Request
from puppy.http.constants import GET, POST, COOKIE, SET_COOKIE, INTEGER

try:
    # Python 2 quote and unquote
    from urllib import quote, unquote
except:
    # Python 3 quote and unquote
    from urllib.parse import quote_from_bytes as quote, unquote_to_bytes as unquote

# Schema constants
SCHEMA_HTTP = b"http"
SCHEMA_HTTPS = b"https"
SCHEMA_MAPPING = {SCHEMA_HTTP: 80, SCHEMA_HTTPS: 443}


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
            request.headers.set(
                COOKIE,
                b"; ".join([
                    # Format as name=value
                    b"%s=%s" % (quote(name).encode(), quote(value).encode())
                    # For each cookie in the jar
                    for name, value in self.cookies.items()
                ]),
            )

        # Return the request
        return request

    def _update_response(self, response):
        # Update cookie jar with response headers
        for header in response.headers.pop(SET_COOKIE):
            # Check if semicolon exists
            if b";" in header:
                # Split by semicolon
                cookie, _ = header.split(b";", 1)
            else:
                # Take as is
                cookie = header

            # Make sure '=' exists
            if b"=" not in cookie:
                continue

            # Split and decode
            name, value = cookie.split(b"=", 1)
            name, value = unquote(name.decode()), unquote(value.decode())

            # Update cookie jar
            self.cookies[name] = value

        # Return the response
        return response

    def get(self, url, *args, **kwargs):
        return self.request(GET, url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self.request(POST, url, *args, **kwargs)

    def wrap(self, connection, host=None):
        # Wrap connection with SSL
        context = ssl.create_default_context()

        # Disable certificate check
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Wrap connection using context
        return context.wrap_socket(connection, server_hostname=host)

    def interface(self, host, port, tls=False):
        # Determine address of host
        address = socket.gethostbyname(host), port

        # Check if interface is closed and remove it
        if address in self.interfaces:
            if self.interfaces[address].closed:
                del self.interfaces[address]

        # Check if interface already exists
        if address not in self.interfaces:
            # Connect to socket
            connection = socket.socket()
            connection.connect(address)

            # Wrap with TLS connection if needed
            if tls:
                connection = self.wrap(connection, host)

            # Create client interface
            self.interfaces[address] = self.implementation(connection)

        # Return interface for address
        return self.interfaces[address]

    def request(self, method, url, headers=[], body=None):
        # Create headers object
        headers = Headers(headers)

        # Parse URL using parser
        schema, host, port, path = urlsplit(url)

        # Add host header if required
        if HOST not in headers:
            if not port:
                headers[HOST] = host
            else:
                headers[HOST] = host + b":" + INTEGER % port

        # Make sure port is defined
        schema = schema or SCHEMA_HTTP
        port = port or SCHEMA_MAPPING[schema]

        # Get interface for request by address and update host
        interface = self.interface(host, port, schema == SCHEMA_HTTPS)

        # Create request object
        request = Request(method, path or b"/", headers, body)

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
