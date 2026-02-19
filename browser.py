from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import DOWNLOAD_DIR, PROFILE_DIR
import os


def get_driver():
    chrome_options = Options()

    # Persistent login session
    chrome_options.add_argument(f"--user-data-dir={PROFILE_DIR}")

    # Disable automation detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Auto download settings
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    }

    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    #

    driver.maximize_window()
    return driver
