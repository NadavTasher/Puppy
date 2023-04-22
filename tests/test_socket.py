import time
import socket
import random
import unittest
import contextlib

from puppy.thread.looper import Looper
from puppy.socket.multiplex import MultiplexSocket
from puppy.socket.stream import MessageStream


class SocketTestCase(unittest.TestCase):

    def test_message_stream(self):
        # Create two sockets
        s1, s2 = socket.socketpair()

        try:
            # Create message streams
            stream1 = MessageStream(s1)
            stream2 = MessageStream(s2)

            # Send a message
            stream1.transmit_message(b"Hello World!")

            # Receive a message on the other end
            assert stream2.receive_message() == b"Hello World!"
        finally:
            # Close the sockets
            s1.close()
            s2.close()

    def test_multiplex(self):

        class MuxHandler(MultiplexSocket):

            received_message = None

            def handle_stream(self, number):
                self.received_message = self.socket(number).recv(1024)

        class MuxLooper(Looper):

            def __init__(self, socket):
                super(MuxLooper, self).__init__()
                self.mux = MuxHandler(socket)

            def loop(self):
                ready = self.select(self.mux.sockets, 0.1)
                self.mux.handle(ready)

        # Create test socket pair
        local_end, remote_end = socket.socketpair()

        # Create both mux sockets
        local_mux = MuxLooper(local_end)
        remote_mux = MuxLooper(remote_end)

        # Start both ends
        local_mux.start()
        remote_mux.start()

        try:
            # Try sending messages
            remote_socket_0 = remote_mux.mux.socket(0)
            local_socket_0 = local_mux.mux.socket(0)
            local_socket_0.sendall(b"Hello")

            # Create another stream
            local_socket_1 = local_mux.mux.socket(1)

            # Make sure remote stream 0 receives message
            assert remote_socket_0.recv(5) == b"Hello"

            # Send a message on the second socket
            local_socket_1.sendall(b"Test!")

            # Sleep some time
            time.sleep(1)

            # Check received message
            assert remote_mux.mux.received_message == b"Test!"
        finally:
            # Stop the mux handlers
            local_mux.stop()
            remote_mux.stop()

            # Close the streams
            local_end.close()
            remote_end.close()
