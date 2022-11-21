import random  # NOQA


def random(length=16, charset="abcdefghijklmnopqrstuvwxyz0123456789"):
    # Create temporary output
    output = str()

    # Loop until length of output is reached
    while len(output) < length:
        output += charset[random.randint(len(charset))]

    # Return the output
    return output


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


def charset(string, charset="abcdefghijklmnopqrstuvwxyz0123456789"):
    # Loop over string
    for char in string:
        # Check if character is in the charset
        if char not in charset:
            return False

    # String is OK
    return True