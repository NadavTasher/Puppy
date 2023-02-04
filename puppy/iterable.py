def undup(iterable):
    # Create output list
    cache = list()

    # Loop over iterable
    for item in iterable:
        # Make sure not duplicate
        if item in cache:
            continue

        # Add the item to the cache
        cache.append(item)

        # Yield the item
        yield item


class Lazy(list):

    def __init__(self, iterable):
        # Set the iterator
        self.iterable = iterable
        self.iterator = iter(self.iterable)

    def __getitem__(self, index):
        # Make sure the list has the item
        try:
            while len(self) <= index:
                # Append the next item
                super(Lazy, self).append(self.iterator.next())
        except StopIteration:
            pass

        # Return the item at the index
        return super(Lazy, self).__getitem__(index)

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.iterable)
