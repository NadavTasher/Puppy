# Import threading classes
from threading import Thread, Event, Lock


class Looper(Thread):
    def __init__(self, parent=None):
        # Initialize internal variables
        self._lock = Lock()
        self._event = Event()
        self._parent = parent

    def loop(self):
        raise NotImplementedError()

    def initialize(self):
        pass

    def finalize(self):
        pass

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

    def run(self):
        try:
            # Initialize looper
            self.initialize()

            # Loop until shutdown
            try:
                while self.running:
                    # Acquire lock before looping
                    with self._lock:
                        self.loop()
            finally:
                # Stop self to kill children
                self.stop()
        finally:
            # Finalize looper
            self.finalize()
