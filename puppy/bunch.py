class Bunch(dict):
    
    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            # Key is not in prototype chain, return it
            return self[key]
    
    def __setattr__(self, key, value):
        try:
            object.__getattribute__(self, key)
        except AttributeError:
            # Convert value to bunch
            if type(value) is dict:
                value = Bunch(value)

            # Set the item
            self[key] = value
        else:
            # Key is in prototype chain, set it
            object.__setattr__(self, key, value)
    
    def __delattr__(self, key):
        try:
            object.__getattribute__(self, key)
        except AttributeError:
            # Delete the item
            del self[key]
        else:
            # Key is in prototype chain, delete it
            object.__delattr__(self, key)