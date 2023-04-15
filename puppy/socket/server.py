import socket
import select

from puppy.thread.looper import Looper

SELECT_TIMEOUT = 0.5


class SocketServer(Looper):

    def __init__(self, addresses):
        # Initialize parent
        super(SocketServer, self).__init__()

        # Set internal state
        self._servers = list()
        self._addresses = addresses

    def loop(self):
        # Check if socket is readable
        servers = self.select(self._servers, SELECT_TIMEOUT)

        # Create a new worker for each socket
        for server in servers:
            # Get address of socket
            address = server.getsockname()

            # Create new worker, hook it to the server and start
            self._addresses[address](self, server).start(self.event)

    def initialize(self):
        # Check if should bind sockets
        if self._servers:
            return

        # Loop over addresses and bind sockets
        for address in self._addresses.keys():
            # Create new server socket
            server = socket.socket()
            server.bind(address)
            server.listen(1)

            # Add server to list
            self._servers.append(server)

    def finalize(self):
        # Close all servers
        for server in self._servers:
            server.close()


class SocketWorker(Looper):

    def __init__(self, parent, server):
        # Initialize parent
        super(SocketWorker, self).__init__()

        # Set daemon property
        self.daemon = True

        # Store connection internally
        self._socket = None
        self._parent = parent
        self._server = server

    def initialize(self):
        try:
            # Accept new connection
            self._socket, address = self._server.accept()

            # Set new name
            self.name = "%s:%d" % address
        except (OSError, IOError):
            # Raise keyboard-interrupt to stop
            raise KeyboardInterrupt()

    def finalize(self):
        # Close socket connection
        if self._socket:
            self._socket.close()
