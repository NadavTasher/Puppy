import time
import select
import unittest
import threading

from puppy.thread.future import future
from puppy.thread.event import Event, select as event_select


class EventTestCase(unittest.TestCase):

    def test_event_select(self):

        @future
        def event_setter(event, timeout):
            time.sleep(timeout)
            event.set()

        # Create target events
        e1 = Event()
        e2 = Event()

        # Run a background event setter
        event_setter(e1, 0.6)

        # Validate expected state
        assert not event_select([e1, e2], 0.1)
        assert not event_select([e1, e2], 0.3)
        assert not event_select([e1, e2], 0)
        assert event_select([e1, e2], 0.3)

    def test_event_fd_select(self):

        @future
        def event_setter(event, timeout):
            time.sleep(timeout)
            event.set()

        # Create target events
        e1 = Event()
        e2 = Event()

        # Run a background event setter
        event_setter(e1, 0.6)

        # Validate expected state
        assert not select.select([e1, e2], [], [], 0.1)[0]
        assert not select.select([e1, e2], [], [], 0.3)[0]
        assert not select.select([e1, e2], [], [], 0)[0]
        assert select.select([e1, e2], [], [], 0.3)[0]

        # Clear the events
        e1.clear()
        e2.clear()

        # Run a background event setter
        event_setter(e1, 0.6)

        # Validate expected state
        assert not select.select([e1, e2], [], [], 0.1)[0]
        assert not select.select([e1, e2], [], [], 0.3)[0]
        assert not select.select([e1, e2], [], [], 0)[0]
        assert select.select([e1, e2], [], [], 0.3)[0]

    def test_event_max_fd(self):
        # Place holder for events
        output = list()

        # Test the maximum fds
        for _ in range(1024):
            output.append(Event())
