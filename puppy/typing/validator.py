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


class validator(object):
    # Wrapper constructor
    def __init__(self, function):
        # Set internal function
        self.function = function

    def __call__(self, value, *args):
        # Run type validation
        return self.function(value, *args)

    def __getitem__(self, args):
        # Make sure arguments are a tuple
        if not check(args, tuple):
            # Change index to be a tuple
            args = tuple([args])

        # Create validation function
        return lambda value: self(value, *args)
