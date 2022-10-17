import os  # NOQA
import tempfile  # NOQA

# Import contextmanager utility
from puppy.utilities.context import contextmanager  # NOQA


def remove(path):
    # Make sure the path exists
    if not os.path.exists(path):
        return

    # Check if the path is a file
    if os.path.isfile(path):
        # Remove the path like a file
        os.remove(path)
    elif os.path.isdir(path):
        # Remove all paths in directory
        for subpath in os.listdir(path):
            remove(subpath)

        # Remove empty directory
        os.rmdir(path)


@contextmanager
def mktemp(*args, **kwargs):
    # Create temporary path
    path = tempfile.mktemp(*args, **kwargs)

    # Try yielding the path
    try:
        yield path
    finally:
        remove(path)
