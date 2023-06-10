import os
import tempfile
import contextlib


def remove(path):
    # Make sure the path exists
    if not os.path.exists(path):
        return

    if os.path.islink(path):
        # Remove the path like a link
        os.unlink(path)
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
def safe(path, *args, **kwargs):
    try:
        # Open and yield the temporary file
        with open(path + "~", *args, **kwargs) as temporary_file:
            yield temporary_file
    except:
        # Remove the temporary file
        remove(path + "~")

        # Reraise the exception
        raise

    # Move the temporary file to the target file
    os.rename(path + "~", path)


@contextlib.contextmanager
def temporary(*args, **kwargs):
    # Create temporary path
    path = tempfile.mktemp(*args, **kwargs)

    # Try yielding the path
    try:
        yield path
    finally:
        remove(path)
