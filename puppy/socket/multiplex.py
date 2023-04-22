import zlib
import struct
import socket
import select
import threading

CHUNK_LENGTH = 0xFFFF
CHUNK_FLAG_ZLIB = 1
CHUNK_FLAG_CLOSE = 2

HEADER_FORMAT = "!HHBx"
HEADER_LENGTH = struct.calcsize(HEADER_FORMAT)

from puppy.socket.wrapper import SocketWrapper


class MultiplexSocket(SocketWrapper):

    def __init__(self, socket):
        # Initialize the parent
        super(MultiplexSocket, self).__init__(socket)

        # Socket management
        self.streams = set()
        self.cli_sockets = dict()
        self.mux_sockets = dict()

        # Create state management locks
        self.rlock = threading.RLock()
        self.wlock = threading.RLock()

    @property
    def sockets(self):
        return [self] + list(self.mux_sockets.values())

    def socket(self, number):
        # Check if stream exists
        if number not in self.streams:
            self.create_stream(number)

        # Return the client socket
        return self.cli_sockets[number]

    def handle_stream(self, number):
        raise NotImplementedError()

    def create_stream(self, number):
        # Make sure stream does not exist
        assert number not in self.streams, "Stream already exists"

        # Create client socket and multiplex socket
        cli_socket, mux_socket = socket.socketpair()

        # Register the sockets where needed
        self.cli_sockets[number] = cli_socket
        self.mux_sockets[number] = mux_socket

        # Add the stream number
        self.streams.add(number)

    def destroy_stream(self, number):
        # Make sure stream exists
        assert number in self.streams, "Stream does not exist"

        # Pop the sockets from their lists and close them
        self.cli_sockets.pop(number).close()
        self.mux_sockets.pop(number).close()

        # Remove the number from the list
        self.streams.remove(number)

    def receive_chunk(self):
        with self.rlock:
            # Receive the header bytes
            header = self.recvexact(HEADER_LENGTH)

            # Unpack the header
            number, length, flags = struct.unpack(HEADER_FORMAT, header)

            # Receive the chunks content
            chunk = self.recvexact(length)

            # Check if compression flag is set
            if flags & CHUNK_FLAG_ZLIB:
                # Decompress the chunk
                chunk = zlib.decompress(chunk)

            # Return the chunk
            return number, chunk, flags & CHUNK_FLAG_CLOSE

    def transmit_chunk(self, number, chunk, close=False):
        # Create initial flags
        flags = 0

        # Check if chunk should be compressed
        if chunk:
            # Add compression flag
            flags |= CHUNK_FLAG_ZLIB

            # Compress the chunk
            chunk = zlib.compress(chunk)

        # Check if close flag should be set
        if close:
            # Add close flag
            flags |= CHUNK_FLAG_CLOSE

        with self.wlock:
            # Pack the header
            header = struct.pack(HEADER_FORMAT, number, len(chunk), flags)

            # Send the header and the chunk
            self.sendall(header)
            self.sendall(chunk)

    def handle(self, readable):
        # Check if should receive a chunk
        if self in readable:
            self.handle_receive()

        # Loop over readable sockets
        for socket in readable:
            self.handle_transmit(socket)

    def handle_receive(self):
        # Receive a single chunk
        number, chunk, close = self.receive_chunk()

        # Check if the stream is a new stream
        if number not in self.streams:
            # Create the new stream
            self.create_stream(number)

            # Write to the mux socket
            self.mux_sockets[number].sendall(chunk)

            # Handle the new stream
            self.handle_stream(number)
        else:
            # Write to the mux socket
            self.mux_sockets[number].sendall(chunk)

        # Check whether should close
        if close:
            self.destroy_stream(number)

    def handle_transmit(self, socket):
        # Find the stream ID
        for number, mux_socket in self.mux_sockets.items():
            # Compare sockets
            if mux_socket is socket:
                break
        else:
            # Stream was not found
            return

        # Try receiving one chunk
        chunk = socket.recv(CHUNK_LENGTH)

        # If chunk is empty, close stream
        if not chunk:
            # Send the closing message
            self.transmit_chunk(number, bytes(), close=True)

            # Destroy the stream
            self.destroy_stream(number)

            # Nothing more to do
            return

        # Transmit the chunk
        self.transmit_chunk(number, chunk)

    def __del__(self):
        # Close all streams
        for number in list(self.streams):
            self.destroy_stream(number)
