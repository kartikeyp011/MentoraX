from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup Chrome
chrome_options = Options()
# Remove headless to see what's happening
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print("Opening Internshala...")
    driver.get("https://internshala.com/internships/computer-science-internship/")

    # Wait for page to load
    time.sleep(5)

    # Save screenshot
    driver.save_screenshot("internshala_debug.png")
    print("✅ Screenshot saved as internshala_debug.png")

    # Save HTML
    with open("internshala_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("✅ HTML saved as internshala_debug.html")

    # Print page title
    print(f"Page title: {driver.title}")

    # Check for common elements
    print("\nChecking for elements...")

    checks = [
        ("individual_internship", "CLASS_NAME"),
        ("internship_meta", "CLASS_NAME"),
        ("container-fluid", "CLASS_NAME"),
        ("profile", "CLASS_NAME"),
    ]

    from selenium.webdriver.common.by import By

    for selector, method in checks:
        try:
            if method == "CLASS_NAME":
                elements = driver.find_elements(By.CLASS_NAME, selector)
            print(f"  ✅ Found {len(elements)} elements with class '{selector}'")
        except Exception as e:
            print(f"  ❌ Error finding '{selector}': {e}")

    input("\nPress Enter to close browser...")

finally:
    driver.quit()