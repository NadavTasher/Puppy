class wrapper(object):
	def __init__(self, target):
		# Set wrapping target
		self._target_ = target

	def __getattr__(self, name):
		# Check if name is target
		if name == "_target_":
			return object.__getattr__(self, name)

		# Check if the wrapping object implements the target
		if hasattr(self, name):
			return object.__getattr__(self, name)
		
		# Return wrapped value
		return getattr(self._target_, name)

	def __setattr__(self, name, value):
		# Check if name is target
		if name == "_target_":
			return object.__setattr__(self, name, value)

		# Check if the wrapping object implements the target
		if hasattr(self, name):
			return setattr(self, name, value)
		
		# Return wrapped value
		return setattr(self._target_, name, value)
