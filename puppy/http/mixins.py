import io  # NOQA
import gzip  # NOQA

# Import required types
from puppy.http.utilities import fetch_header  # NOQA
from puppy.http.types import Header, Artifact  # NOQA
from puppy.http.interface import HTTPReceiver, HTTPTransmitter  # NOQA
from puppy.socket.wrapper import SocketWrapper  # NOQA


class HTTPGzipMixIn(SocketWrapper):
    # Internal supported variable
    compression_support = False


class HTTPGzipReceiverMixIn(HTTPGzipMixIn, HTTPReceiver):
    def receive_artifact(self):
        # Read artifact from parent
        artifact = super(HTTPGzipReceiverMixIn, self).receive_artifact()

        # Update compression support from artifact
        self._update_compression_support(artifact.headers)

        # Check if the gzip encoding was supplied
        content_encoding = fetch_header(CONTENT_ENCODING, artifact.headers)

        # Make sure the encoding was supplied
        if not content_encoding:
            return artifact

        # Make sure that the gzip encoding was provided
        assert compare(content_encoding, GZIP)

        # Decompress content as gzip
        return artifact._replace(content=zlib.decompress(artifact.content, 40))

    def _update_compression_support(self, headers):
        # Update compression support to false
        self.compression_support = False

        # Fetch the accepted encodings
        accepted_encodings = fetch_header(ACCEPT_ENCODING, headers)

        # Check if the header exists
        if not accepted_encodings:
            return

        # Split the header value and loop
        for encoding in accepted_encodings.split(","):
            if compare(encoding.strip(), GZIP):
                # Compression is supported!
                self.compression_support = True


class HTTPGzipTransmitterMixIn(HTTPGzipMixIn, HTTPTransmitter):
    def transmit_request(self, request):
        # Add accept-encoding header
        headers = request.headers
        headers.append(Header(ACCEPT_ENCODING, GZIP))

        # Modify the request
        request = request._replace(headers=headers)

        # Transmit modified request
        return super(HTTPGzipTransmitterMixIn, self).transmit_request(request)

    def transmit_response(self, response):
        # Check if compression is supported
        if self.compression_support and response.content:
            # Add compression header
            headers = response.headers
            headers.append(Header(CONTENT_ENCODING, GZIP))

            # Extract content from response
            content = response.content

            # Compress the content using gzip
            temporary = io.BytesIO()
            with gzip.GzipFile(fileobj=temporary, mode="w") as compressor:
                compressor.write(content)

            # Update content with value
            content = temporary.getvalue()

            # Modify response with updated values
            response = response._replace(headers=headers, content=content)

        # Transmit the response
        return super(HTTPGzipTransmitterMixIn, self).transmit_response(response)


class HTTPConnectionStateMixIn(SocketWrapper):
    # Internal close variable
    should_close = False


class HTTPConnectionStateReceiverMixIn(HTTPConnectionStateMixIn, HTTPReceiver):
    def receive_artifact(self):
        # Receive artifact from headers
        artifact = super(HTTPConnectionStateReceiverMixIn, self).receive_artifact()

        # Update connection state
        self._update_connection_state(artifact.headers)

        # Return the artifact
        return artifact

    def receive_response(self):
        # Receive a response
        response = super(HTTPConnectionStateReceiverMixIn, self).receive_response()

        # Try-finally
        try:
            return response
        finally:
            # Close the socket if needed
            if self.should_close:
                self.close()

    def _update_connection_state(self, headers):
        # Set default should close
        self.should_close = True

        # Fetch connection header
        connection = fetch_header(CONNECTION, headers)

        # If connection header not present, return
        if not connection:
            return

        # Compare header to keepalive
        self.should_close = compare(connection, KEEP_ALIVE)


class HTTPConnectionStateTransmitterMixIn(HTTPConnectionStateMixIn, HTTPTransmitter):
    def transmit_artifact(self, artifact):
        # Add connection state header
        headers = artifact.headers
        headers.append(Header(CONNECTION, CLOSE if self.should_close else KEEP_ALIVE))

        # Update artifact
        artifact = artifact._replace(headers=headers)

        # Write the artifact
        return super(HTTPConnectionStateTransmitterMixIn, self).transmit_artifact(artifact)

    def transmit_response(self, response):
        # Try-finally
        try:
            return super(HTTPConnectionStateTransmitterMixIn, self).transmit_response(response)
        finally:
            # Close the socket if needed
            if self.should_close:
                self.close()
