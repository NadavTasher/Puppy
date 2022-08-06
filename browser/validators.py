# Import utilities
from .utilities import validator


@validator
def form(value):
    # Make sure the given value is a dictionary
    assert isinstance(value, dict)

    # Make sure all names and values are valid
    for item in value.items():
        assert all([string(inner) for inner in item])


@validator
def string(value):
    # Make sure the given string is a string
    assert isinstance(value, str)

    # Make sure the string is of larger length then 0
    assert len(value) > 0

    # Make sure the string is safe
    assert all(map(lambda char: ord(char) >= 0x20, value))
