# Import type classes
from .types import URL

# Import constants
from .constants import PROTOCOLS


def parse(url):
    # Do all of the parsing
    protocol, locator = parse_url(url)
    address, path = parse_locator(locator)
    host, port = parse_address(address)

    # Change port to default if neccesairy
    port = port or PROTOCOLS.get(protocol)

    # Return all parsed things
    return URL(protocol, host, port, path)


def parse_url(url):
    # Make sure locator exists in url
    if ":" in url:
        # Split url to protocol and locator
        protocol, locator = url.split(":", 1)

        # Make sure protocol is supported
        assert protocol.lower() in PROTOCOLS.keys()

        # Strip locator of leading /s
        locator = locator.lstrip("/")

        # Return protocol and locator
        return protocol, locator
    else:
        # Default protocol and locator
        return PROTOCOLS.keys().pop(), string


def parse_locator(locator):
    # Make sure path exists
    if "/" in locator:
        # Split locator to address and path
        address, path = locator.split("/", 1)

        # Add leading / to path
        path = "/" + path

        # Return address and path
        return address, path
    else:
        # Default address and path
        return locator, "/"


def parse_address(address):
    # Make sure port exists
    if ":" in address:
        # Split address to host and port
        host, port = address.split(":", 1)

        # Convert port to integer
        port = int(port)

        # Return host and port
        return host, port
    else:
        # Default host and port
        return address, 0
