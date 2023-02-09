from puppy.typing.check import validate
from puppy.typing.validator import validator


@validator
def Any(value):
    return True


@validator
def Union(value, *value_types):
    # Validate value with types
    return isinstance(value, tuple(value_types))


@validator
def Literal(value, *literal_values):
    # Make sure value exists
    return value in literal_values


@validator
def Optional(value, optional_type=Any):
    # Return if value is none
    if value is None:
        return True

    # Validate further
    return isinstance(value, optional_type)


@validator
def Text(value):
    return isinstance(value, (str, u"".__class__))


@validator
def List(value, item_type=Any):
    # Make sure value is a list
    if not isinstance(value, list):
        return False

    # Loop over value and check items
    for item in value:
        if not isinstance(item, item_type):
            return False
    
    # Validation has passed
    return True


@validator
def Dict(value, key_type=Any, value_type=Any):
    # Make sure value is a dictionary
    if not isinstance(value, dict):
        return False

    # Loop over keys and values and check types
    for key, value in value.items():
        # Validate key type
        if not isinstance(key, key_type):
            return False

        # Validate value type
        if not isinstance(value, value_type):
            return False

    # Validation has passed
    return True


@validator
def Tuple(value, *item_types):
    # Make sure value is a tuple
    if not isinstance(value, tuple):
        return False

    # If types do not exist, return
    if not item_types:
        return True

    # Make sure value is of length
    if len(value) != len(item_types):
        return False

    # Loop over values in tuple and validate them
    for item, item_type in zip(value, item_types):
        if not isinstance(item, item_type):
            return False
    
    # Validation has passed
    return True

@validator
def Schema(value, schema):
    # TODO: implement
    pass

@validator
def Email(value):
    # TODO implement

    # Make sure value is a string
    if not isinstance(value, Text):
        return False

    try:
        # Split into two (exactly)
        address, domain = value.split("@")

        # Make sure address and domain are defined
        if not (address and domain):
            return False

        # Loop over all parts of address
        for part in address.split("."):
            # Make sure part is not empty
            assert part

            # Make sure part matches charset
            validate(part, Charset["abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&'*+/=?^_`{|}~-"])

        # Loop over all parts of domain
        for part in domain.split("."):
            # Make sure part is not empty
            assert part

            # Make sure part matches charset
            validate(part, Charset["abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"])
    except:
        raise TypeError("%r is not an email address" % value)


@validator
def Charset(value, chars):
    # Make sure value is a string
    if not isinstance(value, Text):
        return False

    # Validate charset
    if any(char not in chars for char in value):
        return False

    # Validation has passed
    return True


# Initialize some charsets
ID = Charset["abcdefghijklmnopqrstuvwxyz0123456789"]
Binary = Charset["01"]
Decimal = Charset["0123456789"]
Hexadecimal = Charset["0123456789ABCDEFabcdef"]
