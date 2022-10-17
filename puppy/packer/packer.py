import os  # NOQA
import zlib  # NOQA

SEPARATOR = "/"


def pack(path, ignored=["__pycache__", ".pyc"]):
    # Create temporary output dictionary
    output = dict()

    # Loop over paths in directory
    for name in os.listdir(path):
        # Create subpath from path and name
        subpath = os.path.join(path, name)

        # Make sure name should not be ignored
        if sum([name.endswith(suffix) for suffix in ignored]):
            continue

        # If path is directory, add new directory
        if os.path.isdir(subpath):
            # Recursively pack
            output[name] = pack(subpath)
        elif os.path.isfile(subpath):
            # Read node value and add to dict
            with open(subpath, "rb") as node:
                output[name] = node.read()

    # Return generated output
    return output


def unpack(path, packed):
    # Make sure path does not exist
    assert not os.path.exists(path)

    # Create the directory for the output
    os.mkdir(path)

    # Loop over items in packed dictionary
    for name, value in packed.items():
        # Create subpath of item
        subpath = os.path.join(path, name)

        # Check if value is another directory
        if isinstance(value, dict):
            # Unpack directory with created path
            unpack(subpath, value)
        else:
            # Open subpath for writing
            with open(subpath, "wb") as node:
                # Write all data
                node.write(value)


def resolve(path, packed):
    # Make sure separator exists in path
    if SEPARATOR in path:
        # Split path once and find
        name, subpath = path.split(SEPARATOR, 1)

        # Recursively search
        return resolve(subpath, packed[name])
    else:
        # Fetch the last node
        return packed[path]
