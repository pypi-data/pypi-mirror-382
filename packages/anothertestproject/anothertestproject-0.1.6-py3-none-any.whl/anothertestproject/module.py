import os
import subprocess

def f():
    package_dir = os.path.dirname(__file__)
    binary_path = os.path.join(package_dir, 'binaries', "connector.exe")

    esult = subprocess.run(
            [binary_path],
            capture_output=True,
            text=True,
            timeout=30
        )