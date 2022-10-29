from puppy.http.types import Header, Artifact, Request, Response  # NOQA
from puppy.http.mixins import HTTPCompressionMixin, HTTPConnectionStateMixin  # NOQA
from puppy.http.interface import VERSION  # NOQA


class HTTPServerInterface(HTTPCompressionMixin, HTTPConnectionStateMixin):
    def receive(self):
        # Receive artifact from parent
        artifact = super(HTTPServerInterface, self).receive()

        # Parse HTTP header as request header
        method, location, _ = artifact.header.split(None, 2)

        # Set host variable
        host = None

        # Find host header in headers
        for key, value in artifact.headers:
            if key.lower() == "host":
                host = value

        # Initialize parameters (to be filled from query)
        parameters = dict()

        # Split location to path and query string
        if "?" in location:
            path, query = location.split("?", 1)

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

            # Return created request
            return Request(
                host, method, path, parameters, artifact.headers, artifact.content
            )

        # Return created request
        return Request(host, method, location, None, artifact.headers, artifact.content)

    def transmit(self, response):
        # Create HTTP header
        header = "HTTP/%.1f %d %s" % (VERSION, response.status, response.message)

        # Create an artifact with the header
        artifact = Artifact(header, response.headers, response.content)

        # Transmit artifact
        return super(HTTPServerInterface, self).transmit(artifact)
