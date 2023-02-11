from puppy.typing.validator import validator


@validator
def Any(variable):
    return True


@validator
def Union(variable, *value_types):
    # Validate value with types
    for value_type in value_types:
        if isinstance(variable, value_type):
            return True

    # Validation has failed
    return False


@validator
def Intersection(variable, *value_types):
    # Validate value with types
    for value_type in value_types:
        if not isinstance(variable, value_type):
            return False

    # Validation has passed
    return True


@validator
def Literal(variable, *literal_values):
    # Make sure value exists
    return variable in literal_values


@validator
def Optional(variable, optional_type=Any):
    # Return if value is none
    if variable is None:
        return True

    # Validate further
    return isinstance(variable, optional_type)


@validator
def Text(variable):
    return isinstance(variable, (str, u"".__class__))


@validator
def Bytes(variable):
    return isinstance(variable, bytes)


@validator
def List(variable, item_type=Any):
    # Make sure value is a list
    if not isinstance(variable, list):
        return False

    # Loop over value and check items
    for item in variable:
        if not isinstance(item, item_type):
            return False

    # Validation has passed
    return True


@validator
def Dict(variable, key_type=Any, value_type=Any):
    # Make sure value is a dictionary
    if not isinstance(variable, dict):
        return False

    # Loop over keys and values and check types
    for key, value in variable.items():
        # Validate key type
        if not isinstance(key, key_type):
            return False

        # Validate value type
        if not isinstance(value, value_type):
            return False

    # Validation has passed
    return True


@validator
def Tuple(variable, *item_types):
    # Make sure value is a tuple
    if not isinstance(variable, tuple):
        return False

    # If types do not exist, return
    if not item_types:
        return True

    # Make sure value is of length
    if len(variable) != len(item_types):
        return False

    # Loop over values in tuple and validate them
    for item, item_type in zip(variable, item_types):
        if not isinstance(item, item_type):
            return False

    # Validation has passed
    return True


@validator
def Schema(variable, schema):
    # Make sure variable is a dict
    if not isinstance(variable, dict):
        return False

    # Make sure schema is a dict
    if not isinstance(schema, dict):
        return False

    # Make sure all of the keys exist
    if set(variable.keys()) - set(schema.keys()):
        return False

    # Make sure all items are valid
    for key, value in schema.items():
        # Check if the value is a dict
        if isinstance(value, dict):
            # Validate as schema
            if not isinstance(variable.get(key), Schema[value]):
                return False
        else:
            # Validate as type
            if not isinstance(variable.get(key), value):
                return False

    # Validation has passed
    return True


@validator
def Charset(variable, chars):
    # Make sure value is a string
    if not isinstance(variable, Text):
        return False

    # Validate charset
    if any(char not in chars for char in variable):
        return False

    # Validation has passed
    return True


@validator
def Domain(variable):
    # Make sure value is a string
    if not isinstance(variable, Text):
        return False

    # Split to parts by dot
    parts = variable.split(".")

    # Make sure all parts are not empty
    if not all(parts):
        return False

    # Loop over parts and validate characters
    for part in parts:
        if not isinstance(part.lower(), Charset["abcdefghijklmnopqrstuvwxyz0123456789-"]):
            return False

    # Validation has passed
    return True


@validator
def Email(variable):
    # Make sure value is a string
    if not isinstance(variable, Text):
        return False

    # Split into two (exactly)
    parts = variable.split("@")

    # Make sure the length is 2
    if len(parts) != 2:
        return False

    # Extract address and domain
    address, domain = parts

    # Make sure address and domain are defined
    if not (address and domain):
        return False

    # Make sure the domain is an FQDN
    if not isinstance(domain, Domain):
        return False

    # Make sure the address is valid
    for part in address.split("."):
        # Make sure part is not empty
        if not part:
            return False

        # Make sure part matches charset
        if not isinstance(part, Charset["abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&'*+-/=?^_`{|}~"]):
            return False

    # Validation has passed
    return True


# Initialize some charsets
ID = Charset["abcdefghijklmnopqrstuvwxyz0123456789"]
Binary = Charset["01"]
Decimal = Charset["0123456789"]
Hexadecimal = Charset["0123456789ABCDEFabcdef"]
