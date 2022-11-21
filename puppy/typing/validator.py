class validator(object):
    # Wrapper constructor
    def __init__(self, function):
        # Set internal function
        self.function = function

    def __call__(self, value, *args):
        # Run type validation
        return self.function(value, *args)

    def __getitem__(self, args):
        # Make sure arguments are a tuple
        if not check(args, tuple):
            # Change index to be a tuple
            args = tuple([args])

        # Create validation function
        return lambda value: self(value, *args)
