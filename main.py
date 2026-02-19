from selenium import webdriver
from browser import get_driver
from order_processor import process_until_empty
from rtd_processor import process_pending_rtd

def main():
    driver = get_driver()

    try:
        # Step 1 → Process Pending Labels
        process_until_empty(driver)

        # Step 2 → Process Pending RTD
        process_pending_rtd(driver)

    finally:
        pass  # keep browser open


if __name__ == "__main__":
    main()
