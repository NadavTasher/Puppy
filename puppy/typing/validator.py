class Validator(object):

    def __init__(self, function):
        self.function = function

    def __instancecheck__(self, value):
        # Check type using the function
        return self.function(value)

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
        return self.function.__name__


class Subvalidator(object):

    def __init__(self, validator, *arguments):
        self.validator = validator
        self.arguments = arguments

    def __instancecheck__(self, value):
        # Check type using the function with the arguments
        return self.validator.function(value, *self.arguments)

    def __repr__(self):
        # Return the representation of the validator
        return "%r%s" % (self.validator, str(self.arguments))


# Add lowercase for ease of use
validator = Validator
