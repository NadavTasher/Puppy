import contextlib


@contextlib.contextmanager
def raises(*exceptions):
    try:
        # Yield to execute
        yield

        # Make sure exception was raised
        raise Exception()
    except exceptions:
        # An expected exception was raised
        pass


@contextlib.contextmanager
def suppress(*exceptions):
    try:
        # Yield to execute
        yield
    except exceptions:
        # Ignore known exceptions
        pass
