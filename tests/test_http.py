import io
import time
import socket
import random
import unittest
import contextlib

from utilities import raises

from puppy.simple.http import SafeHTTP, HTTP
from puppy.http.client import HTTPClient
from puppy.http.server import HTTPServer
from puppy.http.router import HTTPRouter
from puppy.http.headers import Headers
from puppy.http.request import Request
from puppy.http.response import Response
from puppy.http.mixins.host import HTTPHostTransmitterMixIn


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

@contextlib.contextmanager
def create_socketpair():
    lsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsocket.bind(("127.0.0.1", 0))
    lsocket.listen(1)

    csocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    csocket.connect(lsocket.getsockname())
    rsocket, _ = lsocket.accept()

    lsocket.close()

    try:
        yield (csocket, rsocket)
    finally:
        csocket.close()
        rsocket.close()

class HTTPTestCase(unittest.TestCase):

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

    def test_headers(self):
        headers = Headers()
        headers[b"Hello"] = b"World"
        assert eval(repr(headers))[b"Hello"] == [b"World"]
        headers[b"hello"] += b"Test"
        assert dict(eval(repr(headers))) == dict(Headers([(b"Hello", [b"World", b"Test"])]))

class HTTPMixInTestCase(unittest.TestCase):

    def test_host_header_transmitter(self):

        request = Request(b"GET", b"/", [], bytes())
        
        receiver = HTTP()
        transmitter = HTTPHostTransmitterMixIn()

        with raises(AttributeError):
            transmitter.transmit_request(io.BytesIO(), request)

        with create_socketpair() as (r, w):
            transmitter.transmit_request(w, request)
            received = receiver.receive_request(r)

            # Make sure host header exists
            assert received.headers[b"Host"] == [("%s:%d" % w.getpeername()).encode()]
