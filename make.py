import os


def remove_init_files(path):
    for name in os.listdir(path):
        # Create subpath from name
        subpath = os.path.join(path, name)

        # Check if path is file or directory
        if os.path.isdir(subpath):
            remove_init_files(subpath)
        else:
            # Check if name is __init__.py
            if name == "__init__.py" or name.endswith(".pyc"):
                os.remove(subpath)


def create_init_files(path):
    for name in os.listdir(path):
        # Create subpath from name
        subpath = os.path.join(path, name)

        # Check if path is file or directory
        if os.path.isdir(subpath):
            # Create init file
            with open(os.path.join(subpath, "__init__.py"), "wb") as f:
                pass

            # Recurse to create more files
            create_init_files(subpath)


def main(path):
    remove_init_files(path)
    create_init_files(path)


if __name__ == "__main__":
    main("./puppy")
