import os
import fcntl
import threading
import contextlib

try:
    # Python2 threading event type
    _Event = threading._Event
except:
    # Python3 threading event type
    _Event = threading.Event


class Event(_Event):

    def __init__(self, *args, **kwargs):
        # Initialize the parent
        super(Event, self).__init__(*args, **kwargs)

        # Initialize the target set
        self.targets = set()

    def set(self, *args, **kwargs):
        # Set the parent
        super(Event, self).set(*args, **kwargs)

        # Set all target events
        while self.targets:
            self.targets.pop().set(*args, **kwargs)

    @contextlib.contextmanager
    def hook(self, events):
        # Make sure all events are of this type
        for event in events:
            if not isinstance(event, Event):
                raise TypeError()

        try:
            # Add our event to the target list
            for event in events:
                event.targets.add(self)

            # Yield for execution
            yield
        finally:
            # Remove our event from the target list
            for event in events:
                if self in event.targets:
                    event.targets.remove(self)


class PipeEvent(Event):

    def __init__(self, *args, **kwargs):
        # Initialize the parent
        super(Event, self).__init__(*args, **kwargs)

        # Create read and write pipes
        self.rfile, self.wfile = os.pipe()

        # Set read pipe non-blocking
        fcntl.fcntl(self.rfile, fcntl.F_SETFL, os.O_NONBLOCK)

    def set(self, *args, **kwargs):
        # Set the parent
        super(Event, self).set(*args, **kwargs)

        # Write some data to the file
        os.write(self.wfile, bytearray(1))

    def clear(self, *args, **kwargs):
        # Clear the parent
        super(Event, self).clear(*args, **kwargs)

        # Read all data from file
        try:
            while os.read(self.rfile, 1):
                pass
        except OSError:
            pass

    def fileno(self):
        return self.rfile


def select(events, timeout):
    # Wait on events
    wait_on_events(events, timeout)

    # Return a list of all set events
    return [event for event in events if event.is_set()]


def wait_on_events(events, timeout):
    # Make sure all events are our type
    for event in events:
        if not isinstance(event, Event):
            raise TypeError()

    # Make sure event list is not empty
    if not events:
        return

    # Check if any of the events are set
    if any(event.is_set() for event in events):
        return

    # Create a new target event
    target = Event()

    # Hook all of the given events
    with target.hook(events):
        target.wait(timeout)
