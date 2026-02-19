import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PENDING_RTD_URL = "https://seller.flipkart.com/index.html#dashboard/my-orders?serviceProfile=seller-fulfilled&shipmentType=easy-ship&orderState=shipments_to_dispatch"

def process_pending_rtd(driver):
    wait = WebDriverWait(driver, 40)

    print("\n========== Moving to Pending RTD Tab ==========")
    driver.get(PENDING_RTD_URL)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(3)

    batch_number = 1

    while True:
        print(f"\n---- RTD Batch {batch_number} ----")

        # Wait for table to load
        wait.until(EC.presence_of_element_located((By.XPATH, "//table")))
        time.sleep(2)

        # Check if no orders left
        if "No data to display" in driver.page_source:
            print("[INFO] No more RTD orders left.")
            break

        # Select all orders (checkbox)
        select_all_checkbox = wait.until(
            EC.element_to_be_clickable((By.XPATH, "(//input[@type='checkbox'])[1]"))
        )
        driver.execute_script("arguments[0].click();", select_all_checkbox)
        time.sleep(1)

        # Click main Mark RTD button
        mark_rtd_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Mark')]"))
        )
        driver.execute_script("arguments[0].click();", mark_rtd_button)
        print("[INFO] Main Mark RTD clicked.")
        time.sleep(2)

        # ✅ Handle popup / top bar Mark RTD button
        try:
            print("[STEP] Waiting for popup container...")
            popup_container = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[8]/div/div/div[3]"))
            )

            popup_mark_rtd = popup_container.find_element(By.XPATH, ".//button[contains(.,'Mark RTD')]")
            driver.execute_script("arguments[0].click();", popup_mark_rtd)
            print("[SUCCESS] Mark RTD clicked inside popup.")
            time.sleep(2)

            # ✅ Refresh page to confirm RTD mark reflected
            print("[INFO] Refreshing page to confirm RTD mark...")
            driver.refresh()
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            time.sleep(2)

        except Exception:
            print("[INFO] No Mark RTD popup appeared.")

        batch_number += 1
        time.sleep(2)  # small wait before next batch

    print("✅ Pending RTD processing completed.")
