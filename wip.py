import time

from puppy.http.client.client import HTTPClient
from puppy.http.server.server import HTTPServer
from puppy.http.server.router import Router
from puppy.http.types import Response

rtr = Router()
rtr.static(".")

@rtr.get("/test")
def handle(request):
	return Response(200, "OK", None, "Hello World!")

@rtr.get("/crash")
def h2(request):
	assert not request

cli = HTTPClient()
srv = HTTPServer(("0.0.0.0", 8000), rtr)

with srv:
	srv.serve_forever()
# srv.join()
# print(cli.get(b"http://example.com/hello"))
