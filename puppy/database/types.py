import os
import json
import hashlib
import threading
import contextlib


class Node(object):

    def __init__(self, path):
        # Create the node's path
        self.path = os.path.join(path, self.__class__.__name__.lower())


class Index(Node):

    def __init__(self, path):
        # Initialize node
        super(Index, self).__init__(path)

        # Create index file lock
        self.lock = threading.RLock()

        # Create index if does not exist
        with self.modify():
            pass

    def read(self):
        # Lock the mutex
        with self.lock:
            # Make sure index exists
            if not os.path.exists(self.path):
                return list()

            # Read index contents
            with open(self.path, "r") as file:
                return json.load(file)

    @contextlib.contextmanager
    def modify(self):
        with self.lock:
            # Read the index
            index = self.read()

            # Yield for modification
            yield index

            # Write to file
            with open(self.path, "w") as file:
                json.dump(index, file)


class Objects(Node):

    def __init__(self, path, locks):
        # Initialize node
        super(Objects, self).__init__(path)

        # Set the lock dictionary
        self.locks = locks

        # Create objects path if it does not exist
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def read(self, name):
        return os.path.join(self.path, hashlib.sha256(name.encode()).hexdigest())

    @contextlib.contextmanager
    def modify(self, name):
        # Create the path
        path = self.read(name)

        # Check mutex for name if it does not exist
        if path not in self.locks:
            self.locks[path] = threading.RLock()

        # Lock the mutex
        with self.locks[path]:
            # Yield the object path
            yield path