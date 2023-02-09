from puppy.typing.check import check


class partial(object):

    def __init__(self, target, arguments):
        # Set internal function
        self._target = target
        self._arguments = arguments

    def __call__(self, value):
        return self._target(value, *self._arguments)

    def __repr__(self):
        return "%r%s" % (self._target, str(list(self._arguments)))

# def validator(function):
#     class Validator(type):
#         @classmethod
#         def __instancecheck__(cls, value):
#             return function(value)

#         @staticmethod
#         def __getitem__(argument):
#             pass
#     return Validator

def validator(function):
    # Create validator object
    class Type(object):
        def __init__(self, *arguments):
            self.arguments = arguments

        def __instancecheck__(self, value):
            print("aaaaa")
            return function(value, *self.arguments)

        def __getitem__(self, argument):
            # Convert index into list
            if isinstance(argument, tuple):
                arguments = list(argument)
            else:
                arguments = [argument]

            # Return a partial validator
            return self.__class__(*arguments)

        def __repr__(self):
            # Check if arguments are present
            if not self.arguments:
                return function.__name__

            # Append arguments to name
            return "%r%s" % (function.__name__, str(list(self.arguments)))
    
    # Return an instance of the type
    return Type()
