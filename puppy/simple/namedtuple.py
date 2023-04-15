import collections

from puppy.typing.types import Any, List, Tuple


def NamedTuple(name, fields):
    # Create namedtuple classtype
    classtype = collections.namedtuple(name, [key for key, _ in fields])

    # Create class that will validate the types
    class namedtuple(classtype):

        def __new__(cls, *args, **kwargs):
            # Initialize namedtuple with values
            self = classtype.__new__(cls, *args, **kwargs)

            # Loop over properties and validate inputs
            for key, value in fields:
                # Check input with validator
                if not isinstance(getattr(self, key), value):
                    raise TypeError("Argument %s in not an instance of %r" % (key, value))

            # Return the created tuple
            return self

    # Return created tuple
    return namedtuple
