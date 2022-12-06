from puppy.typing.check import validate  # NOQA
from puppy.typing.validator import validator  # NOQA

from puppy.utilities.string import charset  # NOQA


@validator
def Any(value):
    pass


@validator
def Union(value, *value_types):
    # Validate value with types
    validate(value, tuple(value_types))


@validator
def Literal(value, *literal_values):
    # Make sure value exists
    if value in literal_values:
        return

    # Raise type error
    raise TypeError("%r does not exist in %r" % (value, literal_values))


@validator
def Optional(value, optional_type=Any):
    # Return if value is none
    if value is None:
        return

    # Validate further
    validate(value, optional_type)


@validator
def Text(value):
    validate(value, (str, "".__class__))


@validator
def List(value, item_type=Any):
    # Make sure value is a list
    validate(value, list)

    # Loop over value and check them
    for item in value:
        validate(item, item_type)


@validator
def Dict(value, key_type=Any, value_type=Any):
    # Make sure value is a dictionary
    validate(value, dict)

    # Loop over keys and values and check types
    for key, value in value.items():
        validate(key, key_type)
        validate(value, value_type)


@validator
def Tuple(value, *item_types):
    # Make sure value is a tuple
    validate(value, tuple)

    # If types do not exist, return
    if not item_types:
        return

    # Make sure value is of length
    if len(value) != len(item_types):
        raise TypeError("%r is invalid (length != %d)" % (value, len(item_types)))

    # Loop over values in tuple and validate them
    for item, item_type in zip(value, item_types):
        validate(item, item_type)


@validator
def Email(value):
    # Make sure value is a string
    validate(value, Text)

    try:
        # Split into two (exactly)
        address, domain = value.split("@")

        # Make sure address and domain are defined
        assert address and domain

        # Loop over all parts of address
        for part in address.split("."):
            # Make sure part is not empty
            assert part

            # Make sure part matches charset
            assert charset(
                part,
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&'*+/=?^_`{|}~-",
            )

        # Loop over all parts of domain
        for part in domain.split("."):
            # Make sure part is not empty
            assert part

            # Make sure part matches charset
            assert charset(part, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")
    except:
        raise TypeError("%r is not an email address" % value)


@validator
def Charset(value, chars):
    # Make sure value is a string
    validate(value, Text)

    # Validate charset
    if not charset(value, chars):
        raise TypeError("%r has an invalid character" % value)


# Initialize some charsets
ID = Charset["abcdefghijklmnopqrstuvwxyz0123456789"]
Binary = Charset["01"]
Decimal = Charset["0123456789"]
Hexadecimal = Charset["0123456789ABCDEFabcdef"]
