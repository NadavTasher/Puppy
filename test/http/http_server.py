from puppy.http.types import Response
from puppy.http.server import HTTPServer


def handler(request):
    return Response(200, b"OK", None, b"Hello World")


server = HTTPServer(handler)
server.start()