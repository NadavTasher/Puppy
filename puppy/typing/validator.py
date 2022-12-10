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


class validator(object):
    # Wrapper constructor
    def __init__(self, target):
        # Set internal function
        self._target = target

    def __call__(self, value, *arguments):
        # Run type validation
        return self._target(value, *arguments)

    def __getitem__(self, index):
        # Convert index into list
        if check(index, tuple):
            arguments = [item for item in index]
        else:
            arguments = [index]

        # Return a partial validator
        return partial(self, arguments)

    def __repr__(self):
        return self._target.__name__
