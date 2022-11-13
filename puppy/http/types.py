# Import collections
import collections

# Import typing library
from puppy.typing.types import List, Optional, Dict, Literal
from puppy.typing.namedtuple import NamedTuple

# Create interface classes
Header = NamedTuple("Header", [("name", str), ("value", str)])
Artifact = NamedTuple(
    "Artifact", [("header", str), ("headers", List[Header]), ("content", Optional[str])]
)

# Create request & response classes
Request = NamedTuple(
    "Request",
    [
        ("host", str),
        ("method", Literal["GET", "POST"]),
        ("location", str),
        ("parameters", Optional[Dict[str, str]]),
        ("headers", Optional[Headers]),
        ("content", Optional[str]),
    ],
)
Response = NamedTuple(
    "Response",
    [
        ("status", int),
        ("message", str),
        ("headers", List[Header]),
        ("content", Optional[str]),
    ],
)

class Headers(object):
    def __init__(self, headers=None):
        # Initialize order list
        self.keys = list()
        self.values = dict()

        # Add all headers
        if headers:
            for name, value in headers:
                self.add_header(name, value)

    def has_header(self, name):
        # Check if name exists
        return name.lower() in self.keys

    def new_header(self, name):
        # Make sure name does not exist
        if self.has_header(name):
            return

        # Create an empty instance
        self.keys.append(name.lower())
        self.values[name.lower()] = (name, list())

    def add_header(self, name, value):
        # Get the values
        values = self.get_header(name)

        # Add value to list
        values.append(value)

        # Update values dictionary
        self.values[name.lower()] = (name, values)

    def set_header(self, name, value):
        # Make sure the name exists
        self.new_header(name)

        # Update values dictionary
        self.values[name.lower()] = (name, [value])

    def get_header(self, name):
        # Make sure the name exists
        self.new_header(name)

        # Fetch the values
        _, values = self.values[name.lower()]

        # Return the values
        return values

    def pop_header(self, name):
        # Fetch the values
        values = self.get_header(name)

        # Remove the header
        self.remove_header(name)

        # Return the values
        return values

    def remove_header(self, name):
        # Make sure the name exists
        if not self.has_header(name):
            return

        # Remove key from list and value from dict
        self.keys.remove(name.lower())
        del self.values[name.lower()]

    def __iter__(self):
        # Loop over all keys
        for lower in self.keys:
            # Fetch real name and values
            name, values = self.values[lower]

            # Loop over values and yield
            for value in values:
                yield Header(name, value)