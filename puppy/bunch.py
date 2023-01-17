class Bunch(dict):

    def __getattr__(self, key):
        # Check if key is a builtin
        if hasattr(super(Bunch, self), key):
            return super(Bunch, self).__getattr__(key)

        # Fetch the value from the dict
        value = super(Bunch, self).__getitem__(key)

        # Check if the value is a dict
        if type(value) is dict:
            # Cast the value to a bunch
            value = self.__class__(value)

            # Update the value in the dict
            self.__setattr__(key, value)

        # Return the value
        return value

    def __delattr__(self, key):
        # Make sure the key is not a builtin
        assert not hasattr(super(Bunch, self), key)
        
        # Delete the dict item
        return super(Bunch, self).__delitem__(key)

    def __setattr__(self, key, value):
        # Make sure the key is not a builtin
        assert not hasattr(super(Bunch, self), key)

        # Check if the value is a dict
        if type(value) is dict:
            value = self.__class__(value)

        # Set the dict item
        return super(Bunch, self).__setitem__(key, value)