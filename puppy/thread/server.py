# Import python modules
import socket
import select

# Import looper classes
from .looper import Looper


class SocketWorker(Looper):
    def __init__(self):
        # Set internal parameters
        self._socket = None

        # Initialize looper class
        super(SocketWorker, self).__init__()

    @property
    def event(self):
        # Check if there is an evnet on the socket
        has_event, _, _ = select.select([self._socket], [], [], 1)

        # Make sure socket has an event
        return bool(has_event)

    def handle(self):
        raise NotImplementedError()

    def loop(self):
        # Check if the worker has an event
        if self.event:
            self.handle()

    def initialize(self):
        # Accept a socket from the parent
        self._socket, _ = self._parent._socket.accept()

    def finalize(self):
        # Make sure connection is set
        if not self._socket:
            return

        # Close connection
        self._socket.close()
        self._socket = None


class SocketServer(SocketWorker):
    def __init__(self, address):
        # Set internal parameters
        self._address = address

        # Initialize looper class
        super(SocketServer, self).__init__()

    def initialize(self):
        # Create socket to listen on
        self._socket = socket.socket()
        self._socket.bind(self._address)
        self._socket.listen(10)

    def handle(self):
        # Create a new worker and start it
        self.child().start()

    def child(self):
        return SocketWorker().adopt(self)
