PORT_SEPARATOR = b":"
PATH_SEPARATOR = b"/"
QUERY_SEPARATOR = b"?"
SCHEMA_SEPARATOR = b"://"
FRAGMENT_SEPARATOR = b"#"


def urlsplit(string):
    # Initialize output variables
    schema, host, port, path = None, None, None, None

    # Check if schema exists
    if SCHEMA_SEPARATOR in string:
        # Split by schema separator
        schema, string = string.split(SCHEMA_SEPARATOR, 1)

    # Check if path exists
    if PATH_SEPARATOR in string:
        # Split by schema separator
        string, path = string.split(PATH_SEPARATOR, 1)

        # Add separator to path
        path = PATH_SEPARATOR + path

    # Check if port exists
    if PORT_SEPARATOR in string:
        # Split by port separator
        host, port = string.split(PORT_SEPARATOR)

        # Convert port to integer
        port = int(port)
    else:
        # The host name is the string
        host = string

    # Return the results
    return schema, host, port, path


def pathsplit(string):
    # Initialize output variables
    path, query, fragment = None, None, None

    # Check if fragment exists
    if FRAGMENT_SEPARATOR in string:
        # Split by fragment separator
        string, fragment = string.split(FRAGMENT_SEPARATOR, 1)

    # Check if query exists
    if QUERY_SEPARATOR in string:
        # Split by query separator
        path, query = string.split(QUERY_SEPARATOR, 1)
    else:
        # The path is the string
        path = string

    # Return the results
    return path, query, fragment