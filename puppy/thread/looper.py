import sys
import logging
import threading

from puppy.thread.event import Event, select


class Looper(threading.Thread, object):

    def __init__(self):
        # Initialize parent
        super(Looper, self).__init__()

        # Create state objects
        self.lock = threading.Lock()

        # Loop killswitch
        self.event = Event()
        self.events = [self.event]

    def start(self, event=None):
        # Update the event
        if event:
            self.events.append(event)

        # Start the thread
        super(Looper, self).start()

    def run(self):
        try:
            # Run initial initialization
            self.initialize()

            # Loop while not stopped
            while not select(self.events, 0):
                # Aqcuire loop lock
                with self.lock:
                    timeout = self.loop()

                # Sleep the required timeout
                self.sleep(timeout)

            # Stopped by event
            logging.debug("Stopped by event")
        except KeyboardInterrupt:
            # Stopped by interrupt
            logging.debug("Stopped by interrupt")
        except:
            # Log the exception
            logging.error("Stopped by exception", exc_info=sys.exc_info())
        finally:
            # Run final de-initialization
            self.finalize()

    def stop(self):
        # Set the stop event
        self.event.set()

    @property
    def stopped(self):
        # Check if thread is alive
        return not self.is_alive()

    def select(self, objects, timeout):
        # Select on all events
        ready = select(self.events + objects, timeout)

        # Check if any of the exit events are set
        if any(event in ready for event in self.events):
            raise KeyboardInterrupt()

        # Return the list of set items
        return ready

    def sleep(self, timeout):
        # Make sure timeout is defined
        if not timeout:
            return

        # Sleep the required time
        if select(self.events, timeout):
            # If the event was set, raise stop
            raise KeyboardInterrupt()

    def restart(self):
        # Acquire the lock and restart
        with self.lock:
            # Finalize the looper
            self.finalize()

            # Initialize the looper
            self.initialize()

    def loop(self):
        pass

    def initialize(self):
        pass

    def finalize(self):
        pass

    def __repr__(self):
        return "<%s name=%r stopped=%r>" % (self.__class__.__name__, self.name, self.stopped)
