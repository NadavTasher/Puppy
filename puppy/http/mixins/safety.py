from puppy.http.protocol import HTTPReceiver
from puppy.socket.utilities import read


class HTTPSafeReceiverMixIn(HTTPReceiver):
    # Variables to determine maximum sizes
    maximum_line_length = 64 * 1024
    maximum_content_length = 16 * 1024 * 1024

    def _receive_line(self, socket):
        # Receive a line using the parent
        line = super(HTTPSafeReceiverMixIn, self)._receive_line(socket)

        # Make sure line is not too long
        assert len(line) < self.maximum_line_length, "Line is too long"

        # Return the line
        return line

    def _receive_content_by_length(self, socket, length):
        # Make sure length is under the maximal
        assert length < self.maximum_content_length, "Content is too long"

        # Return the content by length
        return super(HTTPSafeReceiverMixIn, self)._receive_content_by_length(socket, length)

    def _receive_content_by_chunks(self, socket):
        # Receive by chunks
        buffer = bytes()
        length = int(self._receive_line(socket), 16)

        # Loop until no more chunks
        while length:
            # Make sure length has not reached the maximum
            assert len(buffer) + length < self.maximum_content_length, "Content is too long"

            # Receive the chunk
            buffer += read(socket, length)

            # Read an empty line
            self._receive_line(socket)

            # Receive the next length
            length = int(self._receive_line(socket), 16)

        # Receive the last line
        self._receive_line(socket)

        # Return the buffer
        return buffer

    def _receive_content_by_stream(self, socket, chunk=4096):
        # Initialize reading buffer
        buffer = bytes()
        temporary = socket.recv(chunk)

        # Loop until buffer is full
        while temporary:
            # Append to the buffer
            buffer += temporary

            # Make sure length has not passed the maximum
            assert len(buffer) < self.maximum_content_length, "Content is too long"

            # Receive the next chunk into a temporary buffer
            temporary = socket.recv(chunk)

        # Return the buffer
        return buffer
