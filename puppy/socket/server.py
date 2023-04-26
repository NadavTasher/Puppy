import socket

from puppy.thread.looper import Looper


class SocketServer(Looper):

    def __init__(self, workers):
        # Initialize parent
        super(SocketServer, self).__init__()

        # Set internal state
        self.servers = dict()
        self.workers = workers

    def loop(self):
        # Accept a client for each ready server
        for server in self.select(list(self.servers.keys()), 1):
            try:
                # Accept the new client
                connection, address = server.accept()

                # Create a new worker
                worker = self.servers[server](self, connection)
                worker.name = "%s:%d" % address
                worker.start(self.event)
            except (OSError, IOError):
                # Ignore accept errors
                pass

    def initialize(self):
        # Check if should bind sockets
        if self.servers:
            return

        # Loop over addresses and bind sockets
        for address, implementation in self.workers.items():
            # Create new server socket
            server = socket.socket()
            server.bind(address)
            server.listen(1)

            # Add server to list
            self.servers[server] = implementation

    def finalize(self):
        # Close all servers
        for server in self.servers:
            server.close()


class SocketWorker(Looper):

    def __init__(self, parent, socket):
        # Initialize parent
        super(SocketWorker, self).__init__()

        # Set daemon property
        self.daemon = True

        # Store connection internally
        self.parent = parent
        self.socket = socket

    def handle(self):
        raise NotImplementedError()

    def loop(self):
        try:
            # Check if socket is readable
            if not self.select([self.socket], 1):
                return

        except (IOError, ValueError):
            # In case of this error, stop gracefully
            raise KeyboardInterrupt()

        try:
            # Handle the readable socket
            self.handle()
        except IOError:
            # In case of this error, stop gracefully
            raise KeyboardInterrupt()

    def finalize(self):
        # Close socket connection
        self.socket.close()
