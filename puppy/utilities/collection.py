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
