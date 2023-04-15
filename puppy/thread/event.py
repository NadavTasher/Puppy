import os
import fcntl
import threading
import contextlib

from select import select as select_on_files

try:
    # Python 2 threading event type
    _Event = threading._Event
except:
    # Python 3 threading event type
    _Event = threading.Event


class Event(_Event):

    def __init__(self, *args, **kwargs):
        # Initialize the parent
        super(Event, self).__init__(*args, **kwargs)

        # Initialize the target set
        self.targets = set()

        # Initialize the file descriptors
        self.rfile, self.wfile = None, None

    def set(self):
        # Set the parent
        super(Event, self).set()

        # Set all target events
        while self.targets:
            self.targets.pop().set()

        # Make sure pipe is defined
        if not self.wfile:
            return

        # Write some data to the file
        os.write(self.wfile, bytearray(1))

    def clear(self):
        # Clear the parent
        super(Event, self).clear()

        # Make sure pipe is defined
        if not self.rfile:
            return

        try:
            # Read all data from file
            while os.read(self.rfile, 1):
                pass
        except OSError:
            # Suppress this error
            return

    @contextlib.contextmanager
    def hook(self, events):
        # Make sure all events are of this type
        if not all(isinstance(event, Event) for event in events):
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

    def fileno(self):
        # Check if read descriptor exists
        if self.rfile:
            return self.rfile

        # Create a new pipe
        self.rfile, self.wfile = os.pipe()

        # Check if the event is set
        if self.is_set():
            # Write some data to the file
            os.write(self.wfile, bytearray(1))

        # Set read descriptor non-blocking
        fcntl.fcntl(self.rfile, fcntl.F_SETFL, os.O_NONBLOCK)

        # Return the read descriptor
        return self.rfile

    def __del__(self):
        # Check if a read descriptor is defined
        if self.rfile:
            os.close(self.rfile)

        # Check if a write descriptor is defined
        if self.wfile:
            os.close(self.wfile)


def select(objects, timeout):
    # Check if not all objects are events
    if all(isinstance(item, Event) for item in objects):
        return select_on_events(objects, timeout)

    # Select using system select
    ready, _, _ = select_on_files(objects, [], [], timeout)

    # Return the ready objects
    return ready


def wait_on_events(events, timeout):
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


def select_on_events(events, timeout):
    # Wait on events
    wait_on_events(events, timeout)

    # Return a list of all set events
    return [event for event in events if event.is_set()]
