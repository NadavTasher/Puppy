# Import python modules
import os
import json
import time
import signal
import functools
import subprocess

# Import looper classes
from .looper import Looper


class Process(Looper):
	def __init__(self, command, daemonize=False):
		# Set internal consts
		self._command = command
		self._daemonize = daemonize

		# Set internal variables
		self._buffer = None
		self._process = None

		# Initialize looper class
		super(Process, self).__init__()

	@property
	def command(self):
		# Check if daemonization is required
		if not self._daemonize:
			return self._command

		# Wrap with daemonization
		return functools.reduce(
			lambda command, parameter: command % json.dumps(parameter),
			[
				"sh -c %s",
				"setsid sh -c %s > /dev/null 2>&1 & true",
				"sh -c %s > /dev/null 2>&1 & true",
				"sh -c %s",
				self._command,
			],
		)

	def readlines(self):
		# Loop until buffer is empty
		while self._buffer:
			# Pop one line off the buffer
			yield self._buffer.pop(0)

	def loop(self):
		# Try reading line
		line = self._process.stdout.readline()

		# Check if line is defined
		if line:
			self._buffer.append(line)

		# Sleep minimal amount of time
		time.sleep(0.001)

	def initialize(self):
		# Create the buffer
		self._buffer = list()

		# Create the process
		self._process = subprocess.Popen(
			self.command,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			shell=True,
		)

	def finalize(self):
		# Kill the process
		try:
			os.kill(self._process.pid, signal.SIGTERM)
			os.kill(self._process.pid, signal.SIGKILL)
		except:
			# Ignore kill exception
			pass
		finally:
			# Clear the buffer
			self._buffer = None
