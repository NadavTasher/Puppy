# Import modules
import functools


class wrapper(object):
	def __init__(self, target, bind=None):
		# Set wrapping target
		self.__target__ = target

		# Set binding object
		self.__bind__ = bind or self

	@property
	def target(self):
		# Return clean wrapping target - for direct wrapping
		return self.__target__
	
	@property
	def rebound(self):
		# Create a wrapped target and return it - for "rebound" wrapping (target calls wrapper replacement functions)
		return wrapper(self.__target__, self.__bind__)

	def __rebind__(self, value):
		# Check if function is an instancemethod
		if type(value) == type(self.__rebind__):
			# Create rebound method
			@functools.wraps(value.__func__)
			def rebound(*args, **kwargs):
				# Execute function with wrapper as context
				return value.__func__(self.__bind__, *args, **kwargs)

			# Return rebound method
			return rebound

		# Fallback return value
		return value

	def __getattr__(self, name):
		# Fetch value of attribute
		value = getattr(self.__target__, name)

		# Return rebound value
		return self.__rebind__(value)
