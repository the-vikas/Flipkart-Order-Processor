# 📦 Flipkart Seller Automation Tool

Automated order processing and label generation system for Flipkart Seller Dashboard.

This tool helps sellers automate repetitive tasks such as:

- Selecting pending orders  
- Generating shipping labels  
- Processing labels  
- Handling confirmation popups  
- Downloading PDFs  
- Moving labels into timestamped batch folders  
- Marking orders as RTD (Ready To Dispatch)  

Built using **Python + Selenium**, designed for batch processing and production-level stability.

---

## 🚀 Features

- ✅ Auto-detects pending orders
- ✅ Batch-wise label generation
- ✅ Handles dynamic popups (Confirm / Dimension / RTD)
- ✅ Automatic PDF download detection
- ✅ Safe file handling with:
  - Auto rename if duplicate
  - Windows file lock handling
  - Cross-drive safe file move
- ✅ Refresh logic to verify RTD reflection
- ✅ Retry mechanisms to prevent infinite loops
- ✅ Human-like delays for safer execution
- ✅ Crash-resistant loop design

---

## 🛠 Tech Stack

- Python 3.10+
- Selenium WebDriver
- ChromeDriver (via webdriver-manager)
- OS-level file handling (`shutil`, `pathlib`, `glob`)

---

## 📁 Project Structure

