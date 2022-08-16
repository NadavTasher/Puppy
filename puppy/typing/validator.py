def check(value, validator):
	# Check if type is a type
	if isinstance(validator, type):
		# Check if the value is an instance of the type
		if isinstance(value, validator):
			return True
	elif isinstance(validator, tuple):
		# Loop over all types and check them
		for item in validator:
			if check(value, item):
				return True
	else:
		# Execute validator with value
		if validator(value) in (None, value):
			return True

	# Validation has failed
	return False


def validate(value, validator):
	# Check type using check
	if check(value, validator):
		return

	# Raise type error - validation has failed
	raise TypeError("%r is not an instance of %r" % (value, validator))


class validator(object):
	# Decorator for creating types
	def __init__(self, function):
		self.function = function

	def __call__(self, value):
		# Run validation function
		return self.function(value)

	def __getitem__(self, index):
		# Check if index is not a tuple
		if not check(index, tuple):
			# Change index to be a tuple
			index = tuple([index])

		# Create validation function
		return lambda value: self.function(value, *index)
