from collections import namedtuple


def validate(_type, _value, _raise=True):
    try:
        # Check if type is a type
        if isinstance(_type, type):
            # Check if the value is an instance of the type
            if not isinstance(_value, _type):
                raise TypeError(
                    "{0} is not an instance of {1}".format(_value, _type.__name__)
                )
        else:
            # Execute validator with value
            if _type(_value) not in (None, _value):
                # Generic type error
                raise TypeError("{0} is invalid".format(_type))
    except:
        # Check if raise is true
        if _raise:
            raise

        # Return failure
        return False

    # Return success
    return True


def typedtuple(name, properties):
    # Validate inputs
    validate(str, name)
    validate(List(Tuple(str, Any)), properties)

    # Create namedtuple classtype
    classtype = namedtuple(name, [name for name, _ in properties])

    # Create class that validates the properties
    class TypedTuple(classtype):
        def __new__(cls, *args, **kwargs):
            # Initialize namedtuple with values
            self = classtype.__new__(cls, *args, **kwargs)

            # Loop over properties and validate inputs
            for key, validator in properties:
                # Check input with validator
                validate(validator, getattr(self, key))

            # Initialize the tuple
            return self

    # Return created tuple
    return TypedTuple


def Any(_value):
    pass

def Union(*_types):
    def validator(_value):
        # Make sure type is in types
        for _type in _types:
            if validate(_type, _value, _raise=False):
                return

        # Raise exception
        raise TypeError("{0} is not one of {1}".format(_value, _types))

    # Return created validator
    return validator

def Literal(*_values):
    def validator(_value):
        # Make sure value is in values
        if _value not in _values:
            raise TypeError("{0} not in {1}".format(_value, _values))

    # Return created validator
    return validator


def Optional(_type):
    def validator(_value):
        # Return none if given
        if _value is None:
            return

        # Validate further
        validate(_type, _value)

    # Return created validator
    return validator


def List(_type):
    def validator(_value):
        # Make sure value is a list
        validate(list, _value)

        # Loop over values and check type
        for value in _value:
            validate(_type, value)

    # Return created validator
    return validator


def Tuple(*_types):
    def validator(_value):
        # Make sure value is a tuple
        validate(tuple, _value)

        # Make sure value is of length
        if len(_value) != len(_types):
            raise TypeError(
                "{0} is invalid (length != {1})".format(_value, len(_types))
            )

        # Loop over values in tuple and validate them
        for _type, value in zip(_types, _value):
            validate(_type, value)

    # Return created validator
    return validator


def Dictionary(_key_type, _value_type):
    def validator(_value):
        # Make sure value is a dictionary
        validate(dict, _value)

        # Loop over keys and values and check types
        for key, value in _value.items():
            validate(_key_type, key)
            validate(_value_type, value)

    # Return created validator
    return validator
