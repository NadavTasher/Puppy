import ssl
import socket
import contextlib

from puppy.simple.http import HTTP

from puppy.http.types import Request
from puppy.http.utilities import has_header, pop_header, set_header, split_url
from puppy.http.constants import GET, POST, COOKIE, SET_COOKIE, HOST, INTEGER

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
        self.headers = dict()
        self.history = list()

    def _update_request(self, request):
        # Check if cookies are defined
        if not self.cookies:
            return request

        # Create cookies header
        cookies = b"; ".join([
            # Format as name=value
            b"%s=%s" % (quote(name).encode(), quote(value).encode())
            # For each cookie in the jar
            for name, value in self.cookies.items()
        ])

        # Set cookies header
        set_header(request.headers, COOKIE, cookies)

        # Return the request
        return request

    def _update_response(self, response):
        # Loop over all response cookie headers
        while has_header(response.headers, SET_COOKIE):
            # Pop one set-cookie header
            header = pop_header(response.headers, SET_COOKIE)

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

    @contextlib.contextmanager
    def _create_connection(self, host, port, tls=False):
        # Create a socket
        connection = socket.socket()
        connection.connect((host, port))

        # Wrap socket if needed
        if tls:
            # Wrap connection with SSL
            context = ssl.create_default_context()

            # Disable certificate check
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            # Wrap connection using context
            connection = context.wrap_socket(connection, server_hostname=host)

        try:
            # Yield the socket
            yield connection
        finally:
            # Close the connection
            connection.close()

    def get(self, url, *args, **kwargs):
        return self.request(GET, url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self.request(POST, url, *args, **kwargs)

    def request(self, method, url, headers=None, body=None):
        # Create header list
        headers = headers or list()

        # Parse URL using parser
        schema, host, port, path = split_url(url)

        # Append host header
        headers.append((HOST, host if not port else host + b":" + INTEGER % port))

        # Make sure port is defined
        schema = schema or SCHEMA_HTTP
        port = port or SCHEMA_MAPPING[schema]

        # Create the interface
        interface = self.implementation()

        # Create request object
        request = Request(method, path or b"/", headers, body)
        request = self._update_request(request)

        # Get interface for request by address and update host
        with self._create_connection(host, port, schema == SCHEMA_HTTPS) as connection:
            # Send request and receive response
            interface.transmit_request(connection, request)
            response = interface.receive_response(connection)

        # Update the cookies
        response = self._update_response(response)

        # Add new history item
        self.history.append((request, response))

        # Return response
        return response
