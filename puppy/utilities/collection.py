def undup(iterable):
    # Create output list
    output = list()

    # Loop over iterable
    for item in iterable:
        # Add to output if not already there
        if item not in output:
            output.append(item)

    # Return output
    return output