# Import threading classes
from threading import Thread, Event, Lock


class Looper(Thread):
    def __init__(self, parent=None):
        # Initialize internal variables
        self.lock = Lock()
        self.event = Event()
        self.parent = parent

        # Initialize thread class
        super(Looper, self).__init__()

    def __enter__(self):
        # Initialize self
        self.initialize()

    def __exit__(self, *_):
        # Finalize self
        self.finalize()
        return False

    def loop(self):
        raise NotImplementedError()

    def initialize(self):
        pass

    def finalize(self):
        pass

    @property
    def running(self):
        # Check if event is set
        if self.event.is_set():
            return False

        # Check if parent is running
        if self.parent:
            if not self.parent.running:
                return False

        # Still running!
        return True

    def reset(self):
        # Acquire the lock and restart
        with self.lock:
            # Finalize the looper
            self.finalize()

            # Initialize the looper
            self.initialize()

    def stop(self, wait=False):
        # Set the event
        self.event.set()

        # Wait for the thread to finish
        if wait:
            self.join()

    def run(self):
        # Use context manager
        with self:
            # Loop until shutdown
            try:
                while self.running:
                    # Acquire lock before looping
                    with self.lock:
                        self.loop()
            finally:
                # Stop self to kill children
                self.stop()
