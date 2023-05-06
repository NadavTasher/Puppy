import collections


def NamedTuple(name, fields):
    # Create namedtuple classtype
    classtype = collections.namedtuple(name, [key for key, _ in fields])

    # Create class that will validate the types
    class namedtuple(classtype):

        __name__ = name

        def __new__(cls, *args, **kwargs):
            # Initialize namedtuple with values
            self = classtype.__new__(cls, *args, **kwargs)

            # Loop over properties and validate inputs
            for key, type in fields:
                # Fetch the value
                value = getattr(self, key)

                # Check input with validator
                if not isinstance(value, type):
                    raise TypeError("Argument %s in not an instance of %r - %r" % (key, type, value))

            # Return the created tuple
            return self

    # Return created tuple
    return namedtuple
