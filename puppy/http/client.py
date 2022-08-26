# Import urllib for uri parsing
import urllib

# Import http classes
from .types import Artifact, Request, Response
from .interface import Interface, VERSION

class Client(Interface):
	def receive(self):
		# Receive artifact from parent
		artifact = self._receive_artifact()

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
			location += "?" + "&".join(["%s=%s" % (urllib.quote(name), urllib.quote(value)) for name, value in request.parameters.items()])

		# Create HTTP header
		header = "%s %s HTTP/%.1f" % (request.method, location, VERSION)

		# Create an artifact with the header
		artifact = Artifact(header, request.headers, request.content)

		# Transmit artifact
		return self._transmit_artifact(artifact)