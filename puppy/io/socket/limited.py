import struct

# Import classes
from ...typing import wrapper

class limited(wrapper):
	def __init__(self, io, upstream=None, downstream=None, exceptions=True):
		# Initialize super
		super(limited, self).__init__(io)

		# Set limits and properties
		self.exceptions = exceptions
		self.upstream, self.downstream = upstream, downstream

	def send(self, data):
		# Check if there is an upstream limit
		if self.upstream is not None:
			# Make sure upstream is still allowed
			if not self.upstream:
				self.close(True)

			# Strip data buffer
			data = data[:self.upstream]
			
			# Subtract data to be sent
			self.upstream -= len(data)

		# Send data using target
		self.target.send(data)

	def recv(self, length):
		# Check if there is a downstream limit
		if self.downstream is not None:
			# Make sure downstream is still allowed
			if not self.downstream:
				self.close(True)

			# Strip data buffer
			length = min(length, self.downstream)
			
			# Subtract data to be sent
			self.downstream -= length

		# Receive data using target
		return self.target.recv(length)

	def close(self, error=False):
		try:
			# Set linger sockopt if needed
			if error:
				self.target.setsockopt()
				self.target.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0)
		# Close the socket
		self.target.close()

		# If error is true, raise
		assert not error or not self.exceptions