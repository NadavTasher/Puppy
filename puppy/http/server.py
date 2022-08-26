# Import urllib for uri parsing
import urllib

# Import http classes
from .types import Artifact, Request, Response
from .interface import Interface, VERSION

class Server(Interface):
	def receive(self):
		# Receive artifact from parent
		artifact = self._receive_artifact()

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
				name, value = urllib.unquote(name.strip()), urllib.unquote(value.strip())

				# Add to dictionary
				parameters[name] = value

		# Return created request
		return Request(method, path, parameters, artifact.headers, artifact.content)

	def transmit(self, response):
		# Create HTTP header
		header = "HTTP/%.1f %d %s" % (VERSION, response.status, response.message)

		# Create an artifact with the header
		artifact = Artifact(header, response.headers, response.content)

		# Transmit artifact
		return self._transmit_artifact(artifact)