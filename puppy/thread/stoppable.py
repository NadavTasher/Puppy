import threading  # NOQA


class Stoppable(threading.Thread, object):
    def __init__(self):
        # Initialize parent
        super(Stoppable, self).__init__()

        # Create state objects
        self._lock = threading.Lock()
        self._event = threading.Event()

    def loop(self):
        raise NotImplementedError()

    def run(self):
        try:
            # Loop while not stopped
            while not self.stopped:
                # Aqcuire loop lock
                with self._lock:
                    self.loop()
        finally:
            # Stop anyway
            self.stop()

    @property
    def stopped(self):
        # Check if event is set
        return self._event.is_set()

    def stop(self):
        # Set the event
        self._event.set()

    def __repr__(self):
        return "<%s stopped=%r>" % (self.__class__.__name__, self.stopped)
