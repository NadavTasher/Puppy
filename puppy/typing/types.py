from puppy.typing.check import validate  # NOQA
from puppy.typing.validator import validator  # NOQA


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
