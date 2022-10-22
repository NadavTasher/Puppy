import os


def directories(path):
    for name in os.listdir(path):
        # Create subpath from name
        subpath = os.path.join(path, name)

        # Check if path is a directory
        if os.path.isdir(subpath):
            # Yield recursively
            for item in directories(subpath):
                yield item

            # Yield directory
            yield subpath


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


def clean(path):
    for subpath in directories(path):
        # Skip other pycaches
        if "__pycache__" in subpath:
            remove(subpath)
            continue

        # Loop over files
        for subname in os.listdir(subpath):
            if subname == "__init__.py" or subname.endswith(".pyc"):
                remove(os.path.join(subpath, subname))


def make(path):
    for subpath in directories(path):
        # Create init file
        with open(os.path.join(subpath, "__init__.py"), "wb") as stub:
            pass


def main(path):
    clean(path)
    make(path)


if __name__ == "__main__":
    main("./puppy")
