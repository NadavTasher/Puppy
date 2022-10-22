import time

from puppy.http.types import Response
from puppy.http.server.server import HTTPServer

def handler(request):
	return Response(200, "OK", [], "Hello World!")

server = HTTPServer(("0.0.0.0", 8000), handler)
server.start()

try:
	while True:
		time.sleep(1)
except:
	server.stop()