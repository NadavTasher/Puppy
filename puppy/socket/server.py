try:
    # Python 3 socketserver
    from socketserver import *
except:
    # Python 2 socketserver
    from SocketServer import *

import socket  # NOQA
import select  # NOQA

from puppy.thread.looper import Looper  # NOQA


SELECT_TIMEOUT = 0.5
SOCKET_TIMEOUT = 10


class SocketServer(Looper):
    def __init__(self, address, implementation):
        # Initialize parent
        super(SocketServer, self).__init__()

        # Set internal state
        self._socket = None
        self._address = address
        self._implementation = implementation

    def loop(self):
        # Check if socket is readable
        ready, _, _ = select.select([self._socket], [], [], SELECT_TIMEOUT)

        # Make sure socket is ready
        if not ready:
            return

        # Run new worker thread
        self._implementation(self._socket).start()

    def initialize(self):
        self._socket = socket.socket()
        self._socket.bind(self._address)
        self._socket.listen(1)

    def finalize(self):
        if self._socket:
            self._socket.close()


class SocketWorker(Looper):
    def __init__(self, server):
        # Initialize parent
        super(SocketWorker, self).__init__()

        # Store connection internally
        self._socket = None
        self._server = server

    def initialize(self):
        # Accept new connection
        self._socket, address = self._server.accept()

        # Set new name
        self.name = "%s:%d" % address

    def finalize(self):
        if self._socket:
            self._socket.close()
