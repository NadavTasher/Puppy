# Import inspect for inspections
import inspect


def arguments(function, args, kwargs):
    # Fetch function spec
    info = inspect.getargspec(function)

    # Create dictionary for output
    variables = dict()

    # Fetch argnames and defaults
    argnames = info.args or list()
    defaults = info.defaults or list()
    defaults = dict(zip(argnames[-len(defaults) :], defaults))

    # Add all kwargs to variables
    variables.update(kwargs)

    # Loop over argnames and append args
    for argname, argvalue in zip(argnames, args):
        variables[argname] = argvalue

    # Add missing variables
    for argname in set(argnames) - set(variables.keys()):
        variables[argname] = defaults.get(argname)

    # Create zipped result of all arguments
    return variables
