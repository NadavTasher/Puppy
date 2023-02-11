class Validator(object):

    def __init__(self, function):
        self._function = function

    def __instancecheck__(self, value):
        # Check type using the function
        return self._function(value)

    def __getitem__(self, argument):
        # Convert index into list
        if isinstance(argument, tuple):
            arguments = list(argument)
        else:
            arguments = [argument]

        # Return a partial validator
        return Subvalidator(self, *arguments)

    def __repr__(self):
        # Return the name of the function
        return self._function.__name__


class Subvalidator(object):

    def __init__(self, validator, *arguments):
        self._validator = validator
        self._arguments = arguments

    def __instancecheck__(self, value):
        # Check type using the function with the arguments
        return self._validator._function(value, *self._arguments)

    def __repr__(self):
        # Return the representation of the validator
        return "%r%r" % (self._validator, list(self._arguments))


# Add lowercase for ease of use
validator = Validator
