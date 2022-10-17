class ContextManager(object):
    def __init__(self, generator):
        # Set internal generator
        self.generator = generator

    def __enter__(self):
        # Yield one result from the context manager
        for result in self.generator:
            return result
        
        # Raise an exception if nothing was yielded
        raise Exception()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if not exc_type:
            # Make sure no results are left in generator
            for result in self.generator:
                raise Exception()

            # Return true, no exception is raised
            return True
        
        # Return false, an exception has to be raised
        return False

def contextmanager(function):
    # Create wrapper
    def wrapper(*args, **kwargs):
        # Create context manager from function
        return ContextManager(function(*args, **kwargs))
    
    # Return wrapper
    return wrapper