import os
import tempfile
import contextlib


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
        for name in os.listdir(path):
            remove(os.path.join(path, name))

        # Remove empty directory
        os.rmdir(path)


@contextlib.contextmanager
def temporary(*args, **kwargs):
    # Create temporary path
    path = tempfile.mktemp(*args, **kwargs)

    # Try yielding the path
    try:
        yield path
    finally:
        remove(path)
