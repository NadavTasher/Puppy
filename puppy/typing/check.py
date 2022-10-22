# Import typing utilities
from puppy.typing.validator import validate

# Import six utilities
from puppy.six import arguments


def types(*argtypes, **kwargtypes):
    # Create decorator function
    def decorator(function):
        # Create validator dictionary
        validators = arguments(function, argtypes, kwargtypes)

        # Create wrapper function
        def wrapper(*args, **kwargs):
            # Create variable dictionary
            variables = arguments(function, args, kwargs)

            # Validate all missing arguments
            for key in set(validators.keys()) & set(variables.keys()):
            	validate(variables[key], validators[key])

            # Execute function and return
            return function(*args, **kwargs)

        # Return created wrapper
        return wrapper

    # Return created decorator
    return decorator

