import struct
import socket
import select


class SocketWrapper(object):

    def __init__(self, wrapped):
        # Set internal parameter
        self._chunk = 4096

        # Set internal variables
        self._closed = False
        self._socket = wrapped

    def fileno(self):
        return self._socket.fileno()

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
                raise IOError()

            # Append to buffer
            buffer += temporary

        # Return the buffer
        return buffer

    def recvall(self, timeout=5):
        # Initialize reading buffer
        buffer = bytes()

        # Receive the first chunk
        temporary = self.recv(self._chunk)

        # Loop until nothing left to read
        while temporary and self.wait(timeout):
            # Append chunk to buffer
            buffer += temporary

            # Read next chunk
            temporary = self.recv(self._chunk)

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

    def close(self):
        # Skip if already closed
        if self.closed:
            return

        # Close socket
        self._socket.close()

        # Set the closed flag
        self._closed = True


class SocketReader(SocketWrapper):

    def readuntil(self, needle):
        # Create a reading buffer
        buffer = bytes()

        # Loop until needle in buffer
        while needle not in buffer:
            buffer += self.recvexact(1)

        # Strip the buffer of the separator
        return buffer[:-len(needle)]

    def readline(self, separator):
        return self.readuntil(separator)

    def readlines(self, separator):
        # Read first line
        line = self.readline(separator)

        # Loop while line is not empty
        while line:
            # Yield the received line
            yield line

            # Read the next line
            line = self.readline(separator)


class SocketWriter(SocketWrapper):

    def writeline(self, line, separator):
        # Write line if exists
        if line:
            self.sendall(line)

        # Write line separator
        self.sendall(separator)

    def writelines(self, lines, separator):
        # Loop over lines and send them
        for line in lines:
            self.writeline(line, separator)
