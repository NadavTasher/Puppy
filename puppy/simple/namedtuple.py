import collections


def NamedTuple(name, fields):
    # Create namedtuple classtype
    namedtuple = collections.namedtuple(name, [key for key, _ in fields])

    # Create class that will validate the types
    class typechecker(namedtuple):

        # Modify the __class__ variable so that __repr__ will work
        __class__ = namedtuple

        def __new__(cls, *args, **kwargs):
            # Initialize namedtuple with values
            self = namedtuple.__new__(cls, *args, **kwargs)

            # Loop over properties and validate inputs
            for key, value in fields:
                # Check input with validator
                if not isinstance(getattr(self, key), value):
                    raise TypeError("Argument %s in not an instance of %r" % (key, value))

            # Return the created tuple
            return self

    # Return created tuple
    return typechecker
