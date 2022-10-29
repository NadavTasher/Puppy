# Import looper classes
from puppy.thread.looper import Looper

# Import threading classes
from threading import Thread, Event, Lock


class Future(Thread):
    def __init__(self, function, timeout=None):
        # Set internal variables
        self._args = None
        self._kwargs = None
        self._result = None
        self._exception = None

        # Set state variables
        self._running = False
        self._finished = False

        # Store passed arguments
        self._timeout = timeout
        self._function = function

        # Initialize parent
        super(Future, self).__init__()

    def __call__(self, *args, **kwargs):
        # Make sure not running or finished
        assert not (self._running or self._finished)

        # Set variables for execution
        self._args, self._kwargs = args, kwargs

        # Start thread
        self.start()

        # Return self as result
        return self

    def run(self):
        # Set state variables
        self._running = True

        # Try executing the function with given arguments
        try:
            # Store the returned result
            self._result = self._function(*self._args, **self._kwargs)
        except Exception as exception:
            # Store the raised exception
            self._exception = exception
        finally:
            # Set state variables
            self._running = False
            self._finished = True

    @property
    def running(self):
        return self._running

    @property
    def finished(self):
        return self._finished

    @property
    def result(self):
        # Make sure execution has finished
        if not self._finished:
            # Wait for future to finish
            self.join(self._timeout)

        # Raise if exception was stored
        if self._exception:
            raise self._exception

        # Return the result
        return self._result

    def __invert__(self):
        # Return the result value
        return self.result


def future(function):
    # Create wrapper for function
    def wrapper(*args, **kwargs):
        # Create future and execute function
        return Future(function)(*args, **kwargs)

    # Return wrapper
    return wrapper
