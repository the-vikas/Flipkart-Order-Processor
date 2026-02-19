import shutil
import os
import time

def safe_move_pdf(pdf_path, batch_folder, max_wait=10):
    """
    Production-safe PDF move:
    - Waits for file to unlock
    - Auto-renames if file exists
    - Works across drives
    """

    filename = os.path.basename(pdf_path)
    destination = os.path.join(batch_folder, filename)

    # Wait if file still being written (Windows lock issue)
    start_time = time.time()
    while True:
        try:
            with open(pdf_path, "rb"):
                break
        except PermissionError:
            if time.time() - start_time > max_wait:
                raise Exception("File still locked after waiting.")
            time.sleep(1)

    # Auto rename if exists
    counter = 1
    while os.path.exists(destination):
        name, ext = os.path.splitext(filename)
        destination = os.path.join(batch_folder, f"{name}_{counter}{ext}")
        counter += 1

    shutil.move(pdf_path, destination)
    return destination
