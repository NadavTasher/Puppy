import socket  # NOQA
import select  # NOQA

from puppy.thread.looper import Looper  # NOQA


SELECT_TIMEOUT = 0.5
SOCKET_TIMEOUT = 10


class SocketServer(Looper):
    def __init__(self, addresses):
        # Initialize parent
        super(SocketServer, self).__init__()

        # Set internal state
        self._servers = list()
        self._addresses = addresses

    def create(self, address):
        # Create new server socket
        server = socket.socket()
        server.bind(address)
        server.listen(1)

        return server

    def loop(self):
        # Check if socket is readable
        readable_servers, _, _ = select.select([self._servers], [], [], SELECT_TIMEOUT)

        # Make sure socket is ready
        if not readable_servers:
            return

        # Create a new worker for each socket
        for readable_socket in readable_servers:
            # Get address of socket
            address = readable_socket.getsockname()

            # Create new worker
            worker = self._addresses[address](self, readable_socket)
            worker.start()

    def initialize(self):
        # Loop over addresses
        for address in self._addresses.keys():
            # Create new server
            server = self.create(address)

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
        # Accept new connection
        self._socket, address = self._server._socket.accept()

        # Set new name
        self.name = "%s:%d" % address

    def finalize(self):
        # Close socket connection
        if self._socket:
            self._socket.close()
