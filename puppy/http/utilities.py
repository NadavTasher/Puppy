from puppy.http.constants import PORT, PATH, QUERY, SCHEMA, FRAGMENT


def has_header(headers, name):
    # Loop over headers and find header
    for key, value in headers:
        if key.lower() == name.lower():
            return True

    # Header was not found
    return False


def get_header(headers, name):
    # Loop over headers and find header
    for key, value in headers:
        if key.lower() == name.lower():
            return value

    # Header was not found
    raise KeyError(name)


def pop_header(headers, name):
    # Loop over headers and find header
    for key, value in headers:
        if key.lower() == name.lower():
            # Remove the header
            headers.remove((key, value))

            # Return the value
            return value

    # Header was not found
    raise KeyError(name)


def set_header(headers, name, *values):
    # Loop until no header is found
    while has_header(headers, name):
        pop_header(headers, name)

    # Add the headers
    for value in values:
        add_header(headers, name, value)


def add_header(headers, name, value):
    # Add the header to the list
    headers.append((name, value))


def split_url(string):
    # Initialize output variables
    schema, host, port, path = None, None, None, None

    # Check if schema exists
    if SCHEMA in string:
        # Split by schema separator
        schema, string = string.split(SCHEMA, 1)

    # Check if path exists
    if PATH in string:
        # Split by schema separator
        string, path = string.split(PATH, 1)

        # Add separator to path
        path = PATH + path

    # Check if port exists
    if PORT in string:
        # Split by port separator
        host, port = string.split(PORT)

        # Convert port to integer
        port = int(port)
    else:
        # The host name is the string
        host = string

    # Return the results
    return schema, host, port, path


def split_path(string):
    # Initialize output variables
    path, query, fragment = None, None, None

    # Check if fragment exists
    if FRAGMENT in string:
        # Split by fragment separator
        string, fragment = string.split(FRAGMENT, 1)

    # Check if query exists
    if QUERY in string:
        # Split by query separator
        path, query = string.split(QUERY, 1)
    else:
        # The path is the string
        path = string

    # Return the results
    return path, query, fragment
