import struct
import socket
import select


class SocketWrapper(object):

    def __init__(self, wrapped):
        # Set internal parameter
        self._chunk = 4096
        self._separator = b"\n"

        # Set internal variables
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

    def recvexact(self, length=0):
        # Initialize reading buffer
        buffer = bytes()

        # Loop until buffer is full
        while len(buffer) < length:
            # Receive the next chunk into a temporary buffer
            temporary = self.recv(min(length - len(buffer), self._chunk))

            # Make sure something was read to the temporary buffer
            if not temporary:
                raise socket.error("Closed on remote")

            # Append to buffer
            buffer += temporary

        # Return the buffer
        return buffer

    def recvall(self, timeout=5):
        # Initialize reading buffer
        buffer = bytes()
        temporary = True

        # Loop until nothing left to read
        while temporary and self.wait(timeout):
            # Read new temporary chunk
            temporary = self.recv(self._chunk)

            # Append chunk to buffer
            buffer += temporary

        # Return the buffer
        return buffer

    def recv(self, limit=0):
        return self._socket.recv(limit)

    def sendall(self, buffer):
        # Send the buffer in chunks
        while buffer:
            # Send the current chunk
            self._socket.sendall(buffer[:self._chunk])

            # Remove the chunk from the buffer
            buffer = buffer[self._chunk:]

    def send(self, buffer):
        # Send the buffer in chunks
        while buffer:
            # Send the current chunk
            self._socket.send(buffer[:self._chunk])

            # Remove the chunk from the buffer
            buffer = buffer[self._chunk:]

    def abort(self):
        # Skip if already closed
        if self.closed:
            return

        # Set the linger socket option
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))

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


class SocketReader(SocketWrapper):

    def readline(self):
        # Create a reading buffer
        buffer = bytes()

        # Loop until CRLF in buffer
        while self._separator not in buffer:
            buffer += self.recvexact(1)

        # Strip the buffer of the separator
        return buffer[:-len(self._separator)]

    def readlines(self):
        # Read first line
        line = self.readline()

        # Loop while line is not empty
        while line:
            # Yield the received line
            yield line

            # Read the next line
            line = self.readline()


class SocketWriter(SocketWrapper):

    def writeline(self, line=None):
        # Write line if exists
        if line:
            self.sendall(line)

        # Write line separator
        self.sendall(self._separator)

    def writelines(self, lines=[]):
        # Loop over lines and send them
        for line in lines:
            self.writeline(line)
