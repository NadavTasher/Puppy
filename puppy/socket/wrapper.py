import socket  # NOQA
import select  # NOQA


class SocketWrapper(object):
    def __init__(self, wrapped):
        # Set internal socket
        self._closed = False
        self._socket = wrapped

    @property
    def closed(self):
        return self._closed

    @property
    def peek(self):
        # Select on socket to check if has data
        readable, _, _ = select.select([self._socket], [], [], 0)

        # Check if socket is readable
        return self._socket in readable

    def recv(self, count=0):
        # Initialize reading buffer
        buffer = bytearray()

        # Loop until buffer is full
        while len(buffer) < count:
            # Receive one byte
            buffer += self._socket.recv(1)

        # Return the buffer
        return buffer

    def send(self, buffer):
        # Send the buffer
        self._socket.send(buffer)

    def close(self):
        # Skip if already closed
        if self.closed:
            return

        # Close socket
        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

        # Set the closed flag
        self._closed = True
