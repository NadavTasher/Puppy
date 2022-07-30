def validator(function):
    def wrapper(value):
        try:
            # Try validating the variable
            _ = function(value)

            # Variable was validated
            return value
        except:
            # Raise new exception
            raise Exception("Value '{0}' is not valid".format(value, function.__name__))


@validator
def safestring(value):
    # Make sure the given string is a string
    assert isinstance(string, str)

    # Make sure the string is of larger length then 0
    assert len(string) > 0

    # Make sure the string is safe
    assert all(map(lambda char: ord(char) >= 0x20, string))


@validator
def header(value):
    # Make sure the given header is a list
	assert isinstance(header, (list, tuple))

	# Make sure the list is of length 2
	assert len(header) == 2

	# Make sure all the values in the list are safe strings
	for entry in header:
		# Make sure the variable is set and safe
		safestring(entry)
