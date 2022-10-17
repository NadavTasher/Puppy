import os  # NOQA
import zlib  # NOQA
import base64  # NOQA
import shutil  # NOQA
import tempfile  # NOQA
import subprocess  # NOQA

# Decompress resourcess
COMMAND = "{command}"
FILESYSTEM = "{filesystem}"

if __name__ == "__main__":
    # Create temporary path for filesystem
    path = tempfile.mktemp()

    try:
        # Convert filesystem to packed
        packed = eval(zlib.decompress(base64.b64decode(FILESYSTEM)))

        # Unpack filesystem into path
        unpack(path, packed)

        # Run command using subprocess
        subprocess.Popen(
            COMMAND, stdout=subprocess.NONE, stderr=subprocess.NONE, shell=True
        )
    finally:
        # Remove the path
        if os.path.exists(path):
            shutil.rmtree(path)
