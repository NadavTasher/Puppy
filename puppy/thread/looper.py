# Import threading classes
from threading import Thread, Event, Lock


class Looper(Thread):
    def __init__(self):
        # Initialize internal variables
        self._lock = Lock()
        self._event = Event()
        self._parent = None

        # Initialize thread class
        super(Looper, self).__init__()

    def __repr__(self):
        return "<%s running=%r>" % (self.__class__.__name__, self.running)

    def __enter__(self):
        # Initialize self
        self.initialize()

    def __exit__(self, *args):
        # Finalize self
        self.finalize()
        return False

    def run(self):
        # Use context manager
        with self:
            # Loop until shutdown
            try:
                while self.running:
                    # Acquire lock before looping
                    with self._lock:
                        # Execute single loop
                        self.loop()
            finally:
                # Stop self to kill children
                self.stop()

    @property
    def running(self):
        # Check if event is set
        if self._event.is_set():
            return False

        # Check if parent is running
        if self._parent:
            if not self._parent.running:
                return False

        # Still running!
        return True

    def reset(self):
        # Acquire the lock and restart
        with self._lock:
            # Finalize the looper
            self.finalize()

            # Initialize the looper
            self.initialize()

    def stop(self, wait=False):
        # Set the event
        self._event.set()

        # Wait for the thread to finish
        if wait:
            self.join()

    def adopt(self, parent):
        # Set the new parent and return child
        self._parent = parent
        return self

    def loop(self):
        raise NotImplementedError()

    def initialize(self):
        pass

    def finalize(self):
        pass