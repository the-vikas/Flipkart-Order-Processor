import os
import time

def wait_for_download(directory, timeout=60):
    seconds = 0
    while seconds < timeout:
        files = os.listdir(directory)
        if any(file.endswith(".crdownload") for file in files):
            time.sleep(1)
            seconds += 1
        else:
            return True
    raise TimeoutError("Download did not complete in time")
