def format(string, *args, **kwargs):
    # Create temporary output
    haystack = string

    # Loop over args with iterator
    for index, arg in enumerate(args):
        # Create needle for searching
        needle = "{%d}" % index

        # Loop and replace while theres a needle
        while needle in haystack:
            haystack = haystack.replace(needle, arg)

    # Loop over kwargs with items
    for key, kwarg in kwargs.items():
        # Create needle for searching
        needle = "{%s}" % key

        # Loop and replace while theres a needle
        while needle in haystack:
            haystack = haystack.replace(needle, kwarg)

    # Return formatted haystack
    return haystack


def compare(left, right):
    # Make sure the strings are not the same
    if left == right:
        return True

    # Make sure both sides are defined
    if left is None or right is None:
        return False

    # Compare both sides with lower
    return left.lower() == right.lower()
