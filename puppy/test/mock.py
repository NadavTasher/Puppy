# Import python types
import types

class Mock(object):
	def __init__(self, mocked):
		# Set mocked variable
		self._mocked_ = mocked

	def __contains__(self, key):
		return key in self._mocked_

	def __getattr__(self, key):
		# Fetch value
		value = getattr(self._mocked_, key)

		# Check if value is a function
		if callable(value):
			# Create function wrapper
			def wrapper(*args, **kwargs):
				# Print arguments
				print("Function %r of %r has been called with %r, %r" % (key, self._mocked_, args, kwargs))

				# Call function
				output = value(*args, **kwargs)

				# Print output
				print("Function %r of %r resulted with %r" % (key, self._mocked_, output))

				# Return output
				return output

			# Return function wrapper
			return wrapper
		else:
			# Print value!
			print("Attribute fetched, %s=%r" % (key, value))
		
		# Return value by default
		return value

	def __delattr__(self, key):
		return delattr(self._mocked_, key)

	def __hasattr__(self, key):
		return hasattr(self._mocked_, key)

	def __len__(self):
		return len(self._mocked_)

	def __bool__(self):
		return bool(self._mocked_)