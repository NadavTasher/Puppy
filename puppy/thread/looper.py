import threading  # NOQA

from puppy.thread.stoppable import Stoppable  # NOQA


class Looper(Stoppable):

    def __init__(self):
        # Initialize thread class
        super(Looper, self).__init__()

        # Initialize internal variables
        self._parent = None

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
            # Run inherited function
            super(Looper, self).run()

    @property
    def stopped(self):
        # Check if stoppable stopped
        if super(Looper, self).stopped:
            return True

        # Check if parent is running
        if self._parent:
            if self._parent.stopped:
                return True

        # Still running!
        return False

    def reset(self):
        # Acquire the lock and restart
        with self._lock:
            # Finalize the looper
            self.finalize()

            # Initialize the looper
            self.initialize()

    def adopt(self, parent):
        # Set the new parent and return child
        self._parent = parent
        return self

    def initialize(self):
        pass

    def finalize(self):
        pass
