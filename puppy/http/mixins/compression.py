import io
import gzip

from puppy.http.protocol import HTTPReceiver, HTTPTransmitter
from puppy.http.constants import ACCEPT_ENCODING, CONTENT_ENCODING, GZIP


class HTTPCompressionMixIn(object):
    compression_support = False


class HTTPCompressionReceiverMixIn(HTTPCompressionMixIn, HTTPReceiver):

    def receive_artifact(self, socket, content_expected=True):
        # Read artifact from parent
        artifact = super(HTTPCompressionReceiverMixIn, self).receive_artifact(socket, content_expected)

        # Update compression support from artifact
        self._update_compression_support(artifact.headers)

        # Check if a content encoding was supplied
        if CONTENT_ENCODING not in artifact.headers:
            return artifact

        # Check the content encoding
        (content_encoding,) = artifact.headers.pop(CONTENT_ENCODING)

        # Make sure that the gzip encoding was provided
        assert content_encoding.lower() == GZIP

        # Decompress content as gzip
        with gzip.GzipFile(fileobj=io.BytesIO(artifact.content), mode="rb") as decompressor:
            artifact.content = decompressor.read()

        # Return the artifact
        return artifact

    def _update_compression_support(self, headers):
        # Update compression support to false
        self.compression_support = False

        # Fetch the accepted encodings
        if ACCEPT_ENCODING not in headers:
            return

        # Split the header value and loop
        for accepted_encodings in headers[ACCEPT_ENCODING]:
            for encoding in accepted_encodings.split(b","):
                if encoding.strip().lower() == GZIP:
                    # Compression is supported!
                    self.compression_support = True


class HTTPCompressionTransmitterMixIn(HTTPCompressionMixIn, HTTPTransmitter):

    def transmit_request(self, socket, request):
        # Add accept-encoding header
        request.headers[ACCEPT_ENCODING] = GZIP

        # Transmit modified request
        return super(HTTPCompressionTransmitterMixIn, self).transmit_request(socket, request)

    def transmit_response(self, socket, response):
        # Check if compression is supported
        if self.compression_support and response.content:
            # Set compression header
            response.headers[CONTENT_ENCODING] = GZIP

            # Compress the content using gzip
            temporary = io.BytesIO()
            with gzip.GzipFile(fileobj=temporary, mode="w") as compressor:
                compressor.write(response.content)

            # Update content with value
            response.content = temporary.getvalue()

        # Transmit the response
        return super(HTTPCompressionTransmitterMixIn, self).transmit_response(socket, response)
