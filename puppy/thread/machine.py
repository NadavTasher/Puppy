import sys  # NOQA
import logging  # NOQA
import functools  # NOQA
import threading  # NOQA

from puppy.thread.stoppable import Stoppable  # NOQA


def state(function):

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            # Execute the original function
            return function(*args, **kwargs)
        finally:
            # Increment the counter
            wrapper.count += 1

    # Initialize the counter
    wrapper.count = 0

    # Return the wrapper
    return wrapper


class Machine(Stoppable):

    def __init__(self):
        # Initialize parent
        super(Machine, self).__init__()

        # Create state objects
        self._state = self.start_state
        self._history = list()

    def debug(self, state, reason=None, exception=None):
        # Create printable string
        log = "%s -> %s" % (self.name, state.__name__)

        # Append reason if needed
        if reason:
            log = "%s (%s)" % (log, reason)

        # Append exception if needed
        if exception:
            log = "%s [%s]" % (log, exception)

        # Print the move
        logging.debug(log)

    def next(self, state, reason=None, exception=None):
        # Print the state switch
        self.debug(state, reason, exception)

        # Add history entry
        self._history.append((state, reason, exception))

        # Set the next state
        self._state = state

    def loop(self):
        try:
            # Try handling the next state
            result = self._state()

            # Check if the output is none
            if not result:
                return self.next(
                    self.exit_state,
                    reason="State %s did not return a move" %
                    self._state.__name__,
                )

            # Check if the output is a state
            if not isinstance(result, tuple):
                return self.next(result)

            # Check the length of the result
            assert len(result) in range(
                2,
                4), ("State %s returned an invalid move" % self._state.__name__)

            # Add arguments accordingly
            if len(result) == 2:
                # Untuple to state and reason
                _state, _reason = result

                # Set the next state
                return self.next(_state, reason=_reason)
            elif len(result) == 3:
                # Untuple to state, reason and exception
                _state, _reason, _exception = result

                # Set the next state
                return self.next(_state, reason=_reason, exception=_exception)
        except:
            return self.next(
                self.exit_state,
                reason="An unexpected exception was raised",
                exception=sys.exc_info(),
            )

    @state
    def start_state(self):
        return self.stop_state

    @state
    def stop_state(self):
        return self.exit_state

    @state
    def exit_state(self):
        # Stop the thread
        self.stop()

        # Return same state
        return self.exit_state
