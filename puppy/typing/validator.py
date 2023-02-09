class validator(object):
    def __init__(self, function, *arguments):
        self.function = function
        self.arguments = arguments

    def __instancecheck__(self, value):
        return self.function(value, *self.arguments)

    def __getitem__(self, argument):
        # Convert index into list
        if isinstance(argument, tuple):
            arguments = list(argument)
        else:
            arguments = [argument]

        # Return a partial validator
        return self.__class__(self.function, *arguments)

    def __repr__(self):
        # Check if arguments are present
        if not self.arguments:
            return self.function.__name__

        # Append arguments to name
        return "%r%s" % (self.function.__name__, str(list(self.arguments)))