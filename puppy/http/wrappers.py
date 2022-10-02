# Import gzip and io
import gzip
import StringIO

# Import required classes
from ..typing import wrapper

# Import required types
from .types import Header, Artifact


class HTTPCompressionWrapper(wrapper):
    # Set internal variable
    _compress = False

    def receive(self):
        # Receive HTTP artifact
        artifact = self.target.receive()

        # Set encoding variable
        encoding = None

        # Loop over headers and check them
        for key, value in artifact.headers:
            # Check if accept-encoding is set
            if key.lower() == "accept-encoding":
                # Check if gzip is supported
                self._compress = "gzip" in value

            # Check if content-encoding is set
            if key.lower() == "content-encoding":
                encoding = value

        # Check if encoding was set
        if not encoding:
            return artifact

        # Make sure encoding is gzip
        assert encoding.lower() == "gzip"

        # Decompress content as gzip
        return artifact._replace(content=zlib.decompress(artifact.content, 40))

    def transmit(self, artifact):
        # Check if compression is enabled
        if self._compress:
            # Fetch artifact headers and content
            headers = artifact.headers
            content = artifact.content

            # Add encoding headers
            headers.append(Header("Accept-Encoding", "gzip, deflate"))
            headers.append(Header("Content-Encoding", "gzip"))

            # Compress content using gzip
            temporary = StringIO.StringIO()
            with gzip.GzipFile(fileobj=temporary, mode="w") as compressor:
                compressor.write(content)
            content = temporary.getvalue()

            # Modify artifact with updated values
            artifact = artifact._replace(headers=headers, content=content)

        # Transmit artifact
        return self.target.transmit(artifact)


class HTTPConnectionStateWrapper(wrapper):
    # Set internal variable
    _linger = True

    def receive(self):
        # Receive an artifact
        artifact = self.target.receive()

        # Check connection state header
        for key, value in artifact.headers:
            # Check if connection header was set
            if key.lower() == "connection":
                # Compare header to known close value
                self._linger = value.lower() != "close"
                break
        else:
            # Default - close connection
            self._linger = False

        # Return the artifact
        return artifact

    def transmit(self, artifact):
        # Fetch artifact headers
        headers = artifact.headers

        # Add connection headers as needed
        headers.append(Header("Connection", "keep-alive" if self._linger else "close"))

        # Modify artifact headers
        artifact = artifact._replace(headers=headers)

        # Transmit artifact as needed
        self.target.transmit(artifact)

        # Close socket if needed
        if not self._linger:
            self.close()
