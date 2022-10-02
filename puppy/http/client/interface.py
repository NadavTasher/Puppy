# Import required classes
from ...typing import wrapper

# Import required types
from ..types import Header, Artifact, Request, Response

# Import constants
from ..interface import VERSION

class HTTPClientWrapper(wrapper):
    def receive(self):
        # Receive artifact from parent
        artifact = self.target.receive()

        # Parse HTTP header as response header
        _, status, message = artifact.header.split(None, 2)

        # Convert status to int
        status = int(status)

        # Return created response
        return Response(status, message, artifact.headers, artifact.content)

    def transmit(self, request):
        # Create location string
        location = request.location

        # Check if request parameters have to be added
        if request.parameters:
            location += "?" + "&".join(
                [
                    "%s=%s" % (urllib.quote(name), urllib.quote(value))
                    for name, value in request.parameters.items()
                ]
            )

        # Create HTTP header
        header = "%s %s HTTP/%.1f" % (request.method, location, VERSION)

        # Create header list
        headers = [Header("Host", request.host)] + request.headers

        # Create an artifact with the header
        artifact = Artifact(header, headers, request.content)

        # Transmit artifact
        return self.target.transmit(artifact)