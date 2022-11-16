import socket  # NOQA
import select  # NOQA

from puppy.thread.looper import Looper  # NOQA


class Worker(Looper):
    def __init__(self):
        # Set internal parameters
        self._socket = None

        # Initialize looper class
        super(Worker, self).__init__()

    @property
    def poll(self):
        # Check if there is an event on the socket
        has_event, _, _ = select.select([self._socket], [], [], 1)

        # Make sure socket has an event
        return bool(has_event)

    def handle(self):
        raise NotImplementedError()

    def loop(self):
        # Check if the worker has an event
        if self.poll:
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


class Server(Worker):
    def __init__(self, address, implementation):
        # Set internal parameters
        self._address = address
        self._implementation = implementation

        # Initialize looper class
        super(Server, self).__init__()

    def initialize(self):
        # Create socket to listen on
        self._socket = socket.socket()
        self._socket.bind(self._address)
        self._socket.listen(10)

    def handle(self):
        # Create a new worker and start it
        self._implementation().adopt(self).start()
