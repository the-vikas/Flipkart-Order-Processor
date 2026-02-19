import time
import os
import glob
from datetime import datetime
from PyPDF2 import PdfMerger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import DOWNLOAD_DIR
from utils.file_utils import safe_move_pdf


# ==========================================
# ORDERS PAGE URL
# ==========================================
ORDERS_URL = "https://seller.flipkart.com/index.html#dashboard/my-orders?serviceProfile=seller-fulfilled&shipmentType=easy-ship&orderState=shipments_to_pack"


# ==========================================
# CREATE NEW TIMESTAMP FOLDER
# ==========================================
def create_batch_folder():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    batch_folder = os.path.join(DOWNLOAD_DIR, timestamp)
    os.makedirs(batch_folder, exist_ok=True)
    print(f"[INFO] Created batch folder: {batch_folder}")
    return batch_folder


# ==========================================
# WAIT FOR PDF DOWNLOAD
# ==========================================
def wait_for_pdf_download(timeout=120):
    print("[DEBUG] Waiting for PDF download...")
    start_time = time.time()

    while True:
        pdf_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.pdf"))
        temp_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.crdownload"))

        if pdf_files and not temp_files:
            latest_pdf = max(pdf_files, key=os.path.getctime)
            print("[SUCCESS] PDF downloaded:", latest_pdf)
            return latest_pdf

        if time.time() - start_time > timeout:
            raise Exception("PDF download timeout.")

        time.sleep(1)


# ==========================================
# MERGE PDFs
# ==========================================
def merge_pdfs(batch_folder):

    merged_folder = os.path.join(batch_folder, "merged")
    os.makedirs(merged_folder, exist_ok=True)

    pdf_files = glob.glob(os.path.join(batch_folder, "*.pdf"))

    if not pdf_files:
        print("[INFO] No PDFs found to merge.")
        return

    merger = PdfMerger()

    for pdf in sorted(pdf_files):
        merger.append(pdf)

    merged_path = os.path.join(merged_folder, "merged.pdf")
    merger.write(merged_path)
    merger.close()

    print(f"[SUCCESS] Merged PDF created at: {merged_path}")


# ==========================================
# MAIN FUNCTION
# ==========================================
def process_until_empty(driver):

    wait = WebDriverWait(driver, 40)
    driver.get(ORDERS_URL)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    batch_number = 1
    batch_folder = create_batch_folder()
    no_process_attempts = 0

    while True:

        print(f"\n========== Processing Batch {batch_number} ==========")

        wait.until(EC.presence_of_element_located((By.XPATH, "//table")))
        time.sleep(3)

        # ✅ CHECK FOR NO DATA MESSAGE
        no_data_elements = driver.find_elements(
            By.XPATH, "//*[contains(text(),'No data to display')]"
        )

        if len(no_data_elements) > 0:
            print("[INFO] No orders found in Pending Label tab. Exiting smoothly.")
            break

        # Get rows
        rows = driver.find_elements(By.XPATH, "//table/tbody/tr")

        if len(rows) == 0:
            print("[INFO] No rows found. Exiting.")
            break

        # Select all checkbox
        select_all_checkbox = wait.until(
            EC.element_to_be_clickable((By.XPATH, "(//input[@type='checkbox'])[1]"))
        )
        driver.execute_script("arguments[0].click();", select_all_checkbox)
        time.sleep(2)

        # Click Generate button
        generate_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Generate')]"))
        )
        driver.execute_script("arguments[0].click();", generate_button)
        time.sleep(3)

        batch_number += 1

        # Click Process (with safe detection)
        print("[STEP] Checking if Process button appears...")

        # Small UI settle time (very short)
        time.sleep(2)

        process_buttons = driver.find_elements(
            By.XPATH,
            "//button[contains(.,'Process Label')]"
        )

        if not process_buttons:
            no_process_attempts += 1
            print(f"[INFO] Process button not found. Attempt {no_process_attempts}")

            # If it fails twice → only invalid orders remain
            if no_process_attempts >= 2:
                print("[INFO] No processable orders left.")
                print("All labels processed successfully.")
                print("[INFO] Exiting loop to avoid infinite processing.")
                break

            # Refresh and retry once
            driver.refresh()
            time.sleep(4)
            batch_number += 1
            continue

        # If button found → reset counter
        no_process_attempts = 0

        try:
            process_button = process_buttons[0]

            driver.execute_script("arguments[0].click();", process_button)
            print("[SUCCESS] Process clicked.")

            # ==========================================
            # HANDLE CONFIRM POPUP AFTER PROCESS
            # ==========================================

            try:
                print("[STEP] Waiting for Confirm popup...")

                confirm_button = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(.,'Confirm')]")
                    )
                )
                driver.execute_script("arguments[0].click();", confirm_button)
                print("[SUCCESS] Confirm clicked.")
                time.sleep(3)
            
            except Exception:
                print("[INFO] No Confirm popup appeared.")

        except Exception as e:
            print(f"[WARNING] Could not click Process: {e}")
            driver.refresh()
            batch_number += 1
            continue



        # Handle Dimension Popup Confirm
        try:
            popup = driver.find_elements(By.XPATH, "//*[contains(text(),'You haven')]")
            if popup:
                confirm_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Confirm')]"))
                )
                driver.execute_script("arguments[0].click();", confirm_button)
                time.sleep(3)
        except:
            pass

        # Try auto download first
        try:
            pdf_path = wait_for_pdf_download()

        except Exception:
            print("[WARNING] Auto download failed. Trying manual download with refresh loop...")

            download_success = False
            max_attempts = 3

            for attempt in range(max_attempts):

                try:
                    print(f"[STEP] Manual download attempt {attempt + 1}")

                    # Wait for notification container
                    notification = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//*[@id='sub-app-container']/div[4]/div[1]")
                        )
                    )

                    print("[INFO] Download notification found.")

                    # Find Download button inside notification
                    download_button = notification.find_element(By.XPATH, ".//button")

                    driver.execute_script("arguments[0].click();", download_button)
                    print("[INFO] Download button clicked. Waiting 3 seconds...")
                    time.sleep(3)

                    # Check if file downloaded
                    pdf_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.pdf"))

                    if pdf_files:
                        pdf_path = max(pdf_files, key=os.path.getctime)
                        print(f"[SUCCESS] PDF downloaded: {pdf_path}")
                        download_success = True
                        break

                    print("[INFO] File not detected. Refreshing page...")
                    driver.refresh()
                    time.sleep(4)

                except Exception as e:
                    print(f"[WARNING] Attempt failed: {e}")
                    driver.refresh()
                    time.sleep(4)

            if not download_success:
                print("[ERROR] Manual download failed after retries. Skipping batch.")
                driver.refresh()
                batch_number += 1
                continue



        # Move PDF to timestamp folder
        # destination = os.path.join(batch_folder, os.path.basename(pdf_path))
        # os.rename(pdf_path, destination)
        try:
            moved_path = safe_move_pdf(pdf_path, batch_folder)
            print(f"[SUCCESS] PDF moved to: {moved_path}")
        except Exception as e:
            print(f"[ERROR] Failed to move PDF: {e}")
            driver.refresh()
            continue

        print("[SUCCESS] PDF moved to batch folder.")

        driver.refresh()
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        batch_number += 1

    # After loop ends merge PDFs
    merge_pdfs(batch_folder)

    print("\n[SUCCESS] All available orders processed.")
