import collections


class Vector(list):

    def __iadd__(self, item):
        # Append item to list
        self.append(item)

        # Return self
        return self


class Headers(collections.OrderedDict):

    def _to_name(self, key):
        # Convert key to bytes
        name = bytes(key)

        # Loop over keys and find matching key
        for other in self.keys():
            if other.lower() == name.lower():
                return other

        # Returh the name
        return name

    def __contains__(self, key):
        # Convert name to lower-case
        return super(Headers, self).__contains__(self._to_name(key))

    def __setitem__(self, key, value):
        # Make sure value is a list
        if not isinstance(value, Vector):
            value = Vector([value])

        # Convert name to lower-case
        return super(Headers, self).__setitem__(self._to_name(key), value)

    def __getitem__(self, key):
        # Convert name to lower-case
        return super(Headers, self).__getitem__(self._to_name(key))

    def __delitem__(self, key):
        # Convert name to lower-case
        return super(Headers, self).__delitem__(self._to_name(key))

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, list(self))
