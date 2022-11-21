def check(value, validator):
    # Check if type is a type
    if isinstance(validator, type):
        # Check if the value is an instance of the type
        if isinstance(value, validator):
            return True
    elif isinstance(validator, tuple):
        # Loop over all types and check them
        for item in validator:
            if check(value, item):
                return True
    else:
        # Execute validator with value
        if validator(value) in (None, value):
            return True

    # Validation has failed
    return False


def validate(value, validator):
    # Check type using check
    if check(value, validator):
        return

    # Raise type error - validation has failed
    raise TypeError("%r is not an instance of %r" % (value, validator))


def kwargcheck(**type_kwargs):
    # Create wrapper generator
    def generator(function):
        # Create validator wrapper
        @functools.wraps(function)
        def wrapper(**value_kwargs):
            # Loop over type arguments
            for name, value in type_kwargs.items():
                # Validate the type
                validate(value_kwargs.get(name), value)

            # Call the target function
            return function(**value_kwargs)

        # Return the wrapper
        return wrapper

    # Return the generator
    return generator