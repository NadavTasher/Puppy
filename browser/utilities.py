def bind(function, value):
    # Store initial constructor
    constructor = value.__new__

    def __new__(cls, *args, **kwargs):
        # Construct the wanted object
        self = constructor(cls, *args, **kwargs)
        
        # Validate and return
        return function(self)

    # Update the constructor of passed class
    value.__new__ = __new__
    
    # Return binded class
    return value

def merge(left, right):
	# Make sure they are the same type
	assert type(left) == type(right)

	# Create output dictionary
	merged = dict()

	# Loop over zipped result
	for key in dict(left).keys():
		# Extract values
		left_value, right_value = left[key], right[key]

		# Create output value
		value = None

		# Merge them
		if left_value and not right_value:
			value = left_value
		elif not left_value and right_value:
			value = right_value
		else:
			# Make sure they are the same type
			assert type(left_value) == type(right_value)

			# List merge
			if isinstance(left_value, list):
				value = list()

def validator(function):
	# Create validating wrapper
    def wrapper(value):
        try:
            # Try validating the variable
            _ = function(value)

            # Variable was validated
            return value
        except:
            raise
    
    # Return created wrapper
    return wrapper