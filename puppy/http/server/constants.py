from puppy.http.types import Response

# Create preset responses
NOT_FOUND = Response(404, "Not Found", [], None)
BAD_REQUEST = Response(400, "Bad Request", [], None)
INTERNAL_ERROR = Response(500, "Internal Server Error", [], None)