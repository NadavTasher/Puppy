def write(socket, buffer):
    # Send all of the data
    while buffer:
        # Send as many bytes as possible
        offset = socket.send(buffer)

        # Split the data at the offset
        buffer = buffer[offset:]


def read(socket, length, chunk=4096):
    # Initialize reading buffer
    buffer = bytes()

    # Loop until buffer is full
    while len(buffer) < length:
        # Receive the next chunk into a temporary buffer
        temporary = socket.recv(min(length - len(buffer), chunk))

        # Make sure something was read to the temporary buffer
        if not temporary:
            raise IOError()

        # Append to buffer
        buffer += temporary

    # Return the buffer
    return buffer


def readall(socket, chunk=4096):
    # Initialize reading buffer
    buffer = bytes()
    temporary = socket.recv(chunk)

    # Loop until buffer is full
    while temporary:
        # Append to the buffer
        buffer += temporary

        # Receive the next chunk into a temporary buffer
        temporary = socket.recv(chunk)

    # Return the buffer
    return buffer


def readuntil(socket, needle):
    # Create a reading buffer
    buffer = bytes()

    # Loop until needle in buffer
    while needle not in buffer:
        buffer += read(socket, 1)

    # Strip the buffer of the separator
    return buffer[:-len(needle)]
