import struct  # NOQA
import socket  # NOQA
import select  # NOQA

CHUNK = 4096


class SocketWrapper(object):
    def __init__(self, wrapped):
        # Set internal socket
        self._closed = False
        self._socket = wrapped

    @property
    def closed(self):
        return self._closed

    def wait(self, timeout=0):
        # Select on socket to check if has data
        readable, _, _ = select.select([self._socket], [], [], timeout)

        # Check if socket is readable
        return self._socket in readable

    def recvexact(self, length=0, chunk=CHUNK):
        # Initialize reading buffer
        buffer = bytearray()

        # Loop until buffer is full
        while len(buffer) < length:
            # Receive the next chunk into a temporary buffer
            temporary = self.recv(min(length - len(buffer), chunk))

            # Make sure something was read to the temporary buffer
            if not temporary:
                raise socket.error("Closed on remote")

            # Append to buffer
            buffer += temporary

        # Return the buffer
        return buffer

    def recvall(self, chunk=CHUNK):
        # Initialize reading buffer
        buffer = bytearray()
        temporary = True

        # Loop until nothing left to read
        while temporary:
            # Read new temporary chunk
            temporary = self.recv(chunk)

            # Append chunk to buffer
            buffer += temporary

        # Return the buffer
        return buffer

    def recv(self, limit=0):
        return self._socket.recv(limit)

    def sendall(self, buffer):
        # Send the buffer
        self._socket.sendall(buffer)

    def send(self, buffer):
        # Send the buffer
        self._socket.send(buffer)

    def abort(self):
        # Skip if already closed
        if self.closed:
            return

        # Set the linger socket option
        self._socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0)
        )

        # Close the socket
        self.close()

    def close(self):
        # Skip if already closed
        if self.closed:
            return

        # Close socket
        self._socket.close()

        # Set the closed flag
        self._closed = True
