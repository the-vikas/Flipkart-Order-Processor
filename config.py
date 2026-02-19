import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
LABEL_DIR = os.path.join(BASE_DIR, "labels")
LOG_DIR = os.path.join(BASE_DIR, "logs")
PROFILE_DIR = os.path.join(BASE_DIR, "profile")

ORDER_ID_COLUMN = "Order Id"

FLIPKART_URL = "https://seller.flipkart.com/"
