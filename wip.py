from puppy.http.client.client import HTTPClient
from puppy.http.server.server import HTTPServer
from puppy.http.server.router import Router
from puppy.http.types import Response

rtr = Router()

@rtr.get("/test")
def handle(request):
	return Response(200, "OK", None, "Hello World!")

cli = HTTPClient()
srv = HTTPServer(("0.0.0.0", 8001), rtr)
srv.start()
srv.join()
# print(cli.get("http://example.com/hello"))