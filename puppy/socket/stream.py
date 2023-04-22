import struct

from puppy.socket.wrapper import SocketWrapper

CHUNK_LENGTH = 0xFFFFFFFF

HEADER_FORMAT = "!H"
HEADER_LENGTH = struct.calcsize(HEADER_FORMAT)


class MessageStream(SocketWrapper):

    def receive_length(self):
        # Receive the header bytes
        header = self.recvexact(HEADER_LENGTH)

        # Unpack the header
        (length,) = struct.unpack(HEADER_FORMAT, header)

        # Return the length
        return length

    def transmit_length(self, length):
        # Pack the header
        header = struct.pack(HEADER_FORMAT, length)

        # Transmit the header bytes
        self.sendall(header)

    def receive_message(self):
        # Initialize the buffer and read length
        buffer = bytes()
        length = self.receive_length()

        # Loop until the next length is empty
        while length:
            # Read the current message length
            buffer += self.recvexact(length)

            # Read the next length
            length = self.receive_length()

        # Return the buffer
        return buffer

    def transmit_message(self, buffer):
        # Loop until buffer is empty
        while buffer:
            # Send the current chunk
            chunk, buffer = buffer[:CHUNK_LENGTH], buffer[CHUNK_LENGTH:]

            # Send the length
            self.transmit_length(len(chunk))

            # Send the chunk
            self.sendall(chunk)

        # Send an empty length
        self.transmit_length(len(buffer))
