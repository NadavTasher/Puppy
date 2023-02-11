import unittest

from puppy.http.client import HTTPClient
from puppy.http.server import HTTPServer
from puppy.http.router import HTTPRouter

class HTTPClientTestCase(unittest.TestCase):
	def test_http(self):
		# Create HTTP router for tests
		router = HTTPRouter()
		
		# Register a route for tests
		@router.get("/hello")
		def _route(request):
			return Response(200, "OK", None, "Test passed")

		# Create HTTP server for tests
		server = HTTPServer(router)
		server.

		# Create HTTP client for tests
		client = HTTPClient()
		response = client.get("http://localhost/hello")

		assert response.status == 200

	def run_server_in_new_thread(self):
		pass