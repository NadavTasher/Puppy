from puppy.string.utilities import compare  # NOQA


def fetch_header(name, headers):
    # Loop over headers and find required value
    for header in headers:
        # Compare names
        if compare(name, header.name):
            # Return found value
            return header.value
