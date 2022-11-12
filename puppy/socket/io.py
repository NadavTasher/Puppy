from puppy.socket.wrapper import SocketWrapper  # NOQA

# Default line separator
CRLF = "\r\n"


class SocketReader(SocketWrapper):
    def readline(self, separator=CRLF):
        # Create a reading buffer
        buffer = bytearray()

        # Loop until CRLF in buffer
        while separator not in buffer:
            buffer += self.recv(1)

        # Return the buffer without the CRLF
        return buffer[: -len(separator)]

    def readlines(self, separator=CRLF):
        # Read first line
        line = self.readline(separator=separator)

        # Loop while line is not empty
        while line:
            # Yield the received line
            yield line

            # Read the next line
            line = self.readline(separator=separator)


class SocketWriter(SocketWrapper):
    def writeline(self, line=None, separator=CRLF):
        # Write line if exists
        if line:
            self.send(line)

        # Write line separator
        self.send(separator)

    def writelines(self, lines=[], separator=CRLF):
        # Loop over lines and send them
        for line in lines:
            self.writeline(line, separator=separator)
