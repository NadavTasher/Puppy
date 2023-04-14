import time
import unittest
import threading

from puppy.simple.bunch import Bunch
from puppy.thread.future import future
from puppy.thread.looper import Looper
from puppy.thread.event import Event, select


class TestLooper(Looper):

    count = None

    def initialize(self):
        self.count = 0

    def loop(self):
        # Check counter
        if self.count == 10:
            raise KeyboardInterrupt()

        # Add to counter
        self.count += 1

        # Sleep some time
        return 0.01


class ThreadTestCase(unittest.TestCase):

    def test_future(self):

        @future
        def target(event):
            time.sleep(0.1)
            event.set()

        # Create target event
        event = threading.Event()

        # Fire the target
        instance = target(event)

        # Make sure event was not set
        assert not event.is_set()

        # Wait for thread to finish
        _ = ~instance

        # Make sure event was set
        assert event.is_set()

    def test_looper_start(self):
        # Make sure looper works
        looper = TestLooper()
        looper.start()
        looper.join()

        # Make sure count is 10
        assert looper.count == 10

    def test_looper_stop(self):
        # Make sure looper works
        looper = TestLooper()
        looper.start()
        looper.stop()
        looper.join()

        # Make sure count is 10
        assert looper.count != 10

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
        assert not select([e1, e2], 0.1)
        assert not select([e1, e2], 0.3)
        assert not select([e1, e2], 0)
        assert select([e1, e2], 0.3)
