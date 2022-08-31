# Import urllib for uri parsing
import urllib

# Import http classes
from .types import Artifact, Request, Response
from .protocol import Protocol, header, VERSION, OPTIONS


class Client(object):
    @staticmethod
    def receive(io):
        # Receive artifact from parent
        artifact = Protocol.receive(io)

        # Parse HTTP header as response header
        _, status, message = artifact.header.split(None, 2)

        # Convert status to int
        status = int(status)

        # Return created response
        return Response(status, message, artifact.headers, artifact.content)

    @staticmethod
    def transmit(io, request, options=OPTIONS):
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
        return Protocol.transmit(io, artifact)


class Server(object):
    @staticmethod
    def receive(io):
        # Receive artifact from parent
        artifact = Protocol.receive(io)

        # Parse HTTP header as request header
        method, location, _ = artifact.header.split(None, 2)

        # Initialize parameters (to be filled from query)
        parameters = dict()

        # Split location to path and query string
        path, query = uri.split("?", 1)

        # Parse query if needed
        if query:
            # Split query by amp and parse parameters
            for parameter in query.split("&"):
                # Check if parameter contains "="
                if "=" not in parameter:
                    continue

                # Split parameter
                name, value = parameter.split("=", 1)

                # Parse as encoded parameters
                name, value = urllib.unquote(name.strip()), urllib.unquote(
                    value.strip()
                )

                # Add to dictionary
                parameters[name] = value

        # Find host header in headers
        host = header("Host", artifact.headers)

        # Return created request
        return Request(host, method, path, parameters, artifact.headers, artifact.content)

    @staticmethod
    def transmit(io, response, options=OPTIONS):
        # Create HTTP header
        header = "HTTP/%.1f %d %s" % (VERSION, response.status, response.message)

        # Create an artifact with the header
        artifact = Artifact(header, response.headers, response.content)

        # Transmit artifact
        return Protocol.transmit(io, artifact, options)
