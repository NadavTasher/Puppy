import time
import random
import unittest
import contextlib

from puppy.simple.http import SafeHTTP
from puppy.http.client import HTTPClient
from puppy.http.server import HTTPServer
from puppy.http.router import HTTPRouter
from puppy.http.types.response import Response


@contextlib.contextmanager
def create_server(handler):
    # Randomize two new ports
    http_port, https_port = random.randint(0x400, 0xFFFF), random.randint(0x400, 0xFFFF)

    # Create HTTP server for tests
    server = HTTPServer(handler, http=http_port, https=https_port)

    try:
        # Start the server
        server.initialize()
        server.start()

        # Yield for test
        yield server, http_port, https_port
    finally:
        # Stop the server
        server.stop()
        server.join()


class HTTPClientTestCase(unittest.TestCase):

    def test_server(self):
        # Create test handler
        handler = lambda request: Response(123, bytes(), None, bytes())

        # Create server for test
        with create_server(handler) as (server, http_port, https_port):
            # Send requests using HTTPClient
            client = HTTPClient(SafeHTTP)

            # Send a test request
            response = client.get(b"http://localhost:%d" % http_port)
            assert response.status == 123, response

    def test_router(self):
        # Create HTTP router for tests
        router = HTTPRouter()

        # Register a route for tests
        @router.get(b"/hello")
        def _route(request):
            return b"Hello World"

        # Create server for test
        with create_server(router) as (server, http_port, https_port):
            # Send requests using HTTPClient
            client = HTTPClient(SafeHTTP)

            # Send a test request
            response = client.get(b"http://localhost:%d" % http_port)
            assert response.status == 404, response

            # Send a test request
            response = client.get(b"http://localhost:%d/hello" % http_port)
            assert response.status == 200, response

    def test_client(self):
        # Create HTTP client for tests
        client = HTTPClient(SafeHTTP)

        # Send a test request
        response = client.get(b"https://example.com/")
        assert response.status == 200, response

        # Send a test request
        response = client.get(b"https://github.com/")
        assert response.status == 200, response
