from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

TOPICS = ["python", "machine-learning", "web-development", "data-science"]
BASE_URL = "https://www.coursera.org/search?query={}"


def setup_driver():
    options = Options()
    options.add_argument("--headless=new")  # Headless Chrome
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    return driver


def scrape_coursera():
    driver = setup_driver()
    wait = WebDriverWait(driver, 15)

    for topic in TOPICS:
        print(f"\n--- Scraping topic: {topic} ---\n")
        url = BASE_URL.format(topic)
        driver.get(url)

        try:
            # Wait for course cards to appear
            wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div[data-testid='product-card-cds']")))
        except:
            print("Timeout loading results for topic:", topic)
            continue

        time.sleep(2)
        cards = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='product-card-cds']")
        count = 0

        for card in cards:
            if count >= 10:
                break

            try:
                # Title
                title_elem = card.find_element(By.CSS_SELECTOR, "a > h3")
                title = title_elem.text.strip()

                # URL
                link_elem = card.find_element(By.CSS_SELECTOR, "a")
                url = "https://www.coursera.org" + link_elem.get_attribute("href") \
                    if link_elem.get_attribute("href").startswith("/") else link_elem.get_attribute("href")

                # Provider
                provider_elem = card.find_element(By.CSS_SELECTOR, "div.cds-ProductCard-partners > p")
                provider = provider_elem.text.strip()

                # Description / Skills
                try:
                    desc_elem = card.find_element(By.CSS_SELECTOR, "div.cds-CommonCard-bodyContent > p")
                    description = desc_elem.text.strip()
                except:
                    description = None

                # Price
                try:
                    price_elem = card.find_element(By.CSS_SELECTOR, "span[data-testid='tag-root']")
                    price_text = price_elem.text.strip().lower()
                    if "free" in price_text:
                        price_type = "free"
                        price = 0.0
                    else:
                        price_type = "paid"
                        price = 49.0
                except:
                    price_type = "paid"
                    price = 49.0

                # Rating
                try:
                    rating_elem = card.find_element(By.CSS_SELECTOR, "div.cds-RatingStat-meter > span.css-4s48ix")
                    rating = float(rating_elem.text.strip())
                except:
                    rating = None

                # Level
                try:
                    level_elem = card.find_element(By.CSS_SELECTOR, "div.cds-CommonCard-metadata > p")
                    level_text = level_elem.text.strip()
                    level = level_text.split("·")[0].strip().lower()
                except:
                    level = None

                course_data = {
                    "title": title,
                    "description": description,
                    "url": url,
                    "provider": provider,
                    "price_type": price_type,
                    "price": price,
                    "rating": rating,
                    "level": level
                }

                print(course_data)
                count += 1
                time.sleep(2)  # delay between courses

            except Exception as e:
                print("Error parsing a course:", e)
                continue

        time.sleep(3)  # delay between topics

    driver.quit()


if __name__ == "__main__":
    scrape_coursera()