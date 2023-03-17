import sys
import logging
import threading


class Looper(threading.Thread, object):

    def __init__(self):
        # Initialize parent
        super(Looper, self).__init__()

        # Create state objects
        self.lock = threading.Lock()

        # Loop killswitch
        self.event = threading.Event()

    def start(self, event=None):
        # Update the event
        # TODO: orevent
        self.event = event or self.event

        # Start the thread
        super(Looper, self).start()

    def run(self):
        try:
            # Run initial initialization
            self.initialize()

            # Loop while not stopped
            while not self.event.is_set():
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
            logging.error("Stopped by exception:", exc_info=sys.exc_info())
        finally:
            # Set the stop event
            self.stop()

            # Run final de-initialization
            self.finalize()

    def stop(self):
        # Set the stop event
        self.event.set()

    @property
    def stopped(self):
        # Check if thread is alive
        return not self.is_alive()

    def sleep(self, timeout):
        # Make sure timeout is defined
        if not timeout:
            return

        # Sleep the required time
        if self.event.wait(timeout):
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
