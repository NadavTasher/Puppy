import functools


def kwargcheck(**type_kwargs):

    # Generate a decorator factory
    def factory(function):

        # Generate a wrapper
        @functools.wraps(function)
        def wrapper(*value_args, **value_kwargs):
            # Loop over type arguments
            for name, value in type_kwargs.items():
                # Validate the type
                if not isinstance(value_kwargs.get(name), value):
                    raise TypeError("Argument %s is not an instance of %r" % (name, value))

            # Call the target function
            return function(*value_args, **value_kwargs)

        # Return the generated wrapper
        return wrapper

    # Return the generated factory
    return factory
