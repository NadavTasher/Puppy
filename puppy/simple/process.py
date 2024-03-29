import os
import json
import time
import logging
import threading
import functools
import subprocess

from puppy.thread.future import future


def run(command, shell="/bin/sh"):
    # Check if the shell exists
    if os.path.exists(shell):
        # Create a process with proper shell
        return subprocess.Popen([shell, "-c", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Create a process with default shell
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


def timeout(process, seconds=None):
    # If timeout is not defined, return
    if not seconds:
        return

    # Create timeout function
    def target():
        # Sleep the amounted timeout
        time.sleep(seconds)

        # Terminate process if running
        if process.poll() is None:
            process.kill()
            process.terminate()

    # Create new timeout thread
    thread = threading.Thread(target=target)
    thread.start()


def execute(command, check=True, seconds=None):
    # Create process using utility
    process = run(command)

    # Add thread timeout if needed
    if seconds:
        timeout(process, seconds)

    try:
        # Communicate with process
        stdout, stderr = process.communicate()

        # Check if status code should be checked
        if check:
            # Make sure status was OK or raise error
            assert process.returncode == 0, stderr

        # Return the output
        return stdout
    finally:
        # Terminate the process
        if process.poll() is None:
            process.kill()
            process.terminate()


@future
@functools.wraps(execute)
def detached(*args, **kwargs):
    return execute(*args, **kwargs)
