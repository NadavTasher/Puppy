from puppy.http.protocol import HTTPReceiver


class HTTPSafeReceiverMixIn(HTTPReceiver):
    # Variables to determine maximum sizes
    maximum_readuntil = 4 * 1024
    maximum_recvall = 4 * 1024 * 1024
    maximum_recvexact = 64 * 1024 * 1024

    def __init__(self, wrapped, timeout=60):
        # Initialize parent
        super(HTTPSafeReceiverMixIn, self).__init__(wrapped)

        # Set a socket timeout
        self._socket.settimeout(timeout)

    def recvexact(self, length=0):
        # Make sure the length is not larger then maxlength
        assert length < self.maximum_recvexact, "Chunk is too long"

        # Receive using parent
        return super(HTTPSafeReceiverMixIn, self).recvexact(length)

    def recvall(self):
        # Initialize reading buffer
        buffer = bytes()
        temporary = True

        # Loop until nothing left to read
        while temporary:
            # Make sure buffer is not too long
            assert len(buffer) < self.maximum_recvall, "Buffer is too long"

            # Read new temporary chunk
            temporary = self.recv(self._chunk)

            # Append chunk to buffer
            buffer += temporary

        # Return the buffer
        return buffer

    def readuntil(self, needle):
        # Create a reading buffer
        buffer = bytes()

        # Loop until needle in buffer
        while needle not in buffer:
            # Make sure buffer not too long
            assert len(buffer) < self.maximum_readuntil, "Buffer is too long"

            # Receive the next byte
            buffer += self.recvexact(1)

        # Strip the buffer of the separator
        return buffer[:-len(needle)]
