from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from backend.scraper_utils import ScraperBase, OpportunityInserter
from datetime import datetime, timedelta
import time
import re


class InternshalaRealScraper(ScraperBase):
    """Real Internshala scraper using Selenium"""

    def __init__(self):
        super().__init__("Internshala")
        self.driver = None
        self.base_url = "https://internshala.com"

    def setup_driver(self):
        """Setup Selenium Chrome driver"""
        print("🔧 Setting up Chrome driver...")

        chrome_options = Options()
        chrome_options.add_argument('----headless=new')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument(f'user-agent={self.get_random_user_agent()}')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print("✅ Chrome driver ready")

    def close_driver(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

    def scrape(self, max_pages=2, category='computer-science'):
        """
        Scrape internships from Internshala

        Args:
            max_pages: Number of pages to scrape (default 2)
            category: Category to scrape (computer-science, web-development, etc.)
        """
        print(f"🔍 Starting real {self.source_name} scraper...")
        print(f"📂 Category: {category}, Pages: {max_pages}")

        try:
            self.setup_driver()

            # Navigate to internships page
            url = f"{self.base_url}/internships/{category}-internship/"
            print(f"🌐 Opening: {url}")
            self.driver.get(url)

            # Wait for page load
            time.sleep(3)

            for page_num in range(1, max_pages + 1):
                print(f"\n📄 Scraping page {page_num}/{max_pages}...")

                # Extract internships from current page
                internships = self.extract_internships_from_page()

                self.stats['found'] += len(internships)
                print(f"   Found {len(internships)} internships on this page")

                # Process each internship
                for internship in internships:
                    self.process_internship(internship)

                # Try to go to next page
                if page_num < max_pages:
                    if not self.go_to_next_page():
                        print("⚠️  No more pages available")
                        break
                    time.sleep(2)

            # Log and print stats
            self.log_scraping('opportunities', 'success')
            self.print_stats()

        except Exception as e:
            print(f"❌ Scraping error: {e}")
            self.log_scraping('opportunities', 'failed', str(e))
        finally:
            self.close_driver()

    def extract_internships_from_page(self):
        """Extract all internship cards from current page"""
        internships = []

        try:
            # Wait for internship cards to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "individual_internship"))
            )

            # Find all internship cards
            cards = self.driver.find_elements(By.CLASS_NAME, "individual_internship")

            for card in cards:
                try:
                    internship = self.extract_internship_data(card)
                    if internship:
                        internships.append(internship)
                except Exception as e:
                    print(f"   ⚠️  Error extracting card: {e}")
                    continue

        except Exception as e:
            print(f"   ❌ Error finding internship cards: {e}")

        return internships

    def extract_internship_data(self, card):
        """Extract data from a single internship card - Robust version"""
        try:
            # Get all text from card as fallback
            card_text = card.text

            # Title and link - Multiple attempts
            title = None
            link = None

            # Attempt 1: Look for any anchor tag in card
            try:
                all_links = card.find_elements(By.TAG_NAME, "a")
                for a_tag in all_links:
                    href = a_tag.get_attribute('href')
                    if href and '/internship/detail/' in href:
                        link = href
                        title_candidate = a_tag.text.strip()
                        if title_candidate and len(title_candidate) > 10:
                            title = title_candidate
                            break
            except:
                pass

            # Attempt 2: Use profile class
            if not title:
                try:
                    profile_elem = card.find_element(By.CLASS_NAME, "profile")
                    title = profile_elem.text.strip()
                except:
                    pass

            # If still no title/link, skip this card
            if not title or not link:
                return None

            # Ensure link is absolute
            if not link.startswith('http'):
                link = self.base_url + link

            # Company - try multiple methods
            company = "Not specified"
            try:
                company_elem = card.find_element(By.CLASS_NAME, "company_name")
                company = company_elem.text.strip()
            except:
                # Try to extract from card text
                if "at " in card_text:
                    parts = card_text.split("at ")
                    if len(parts) > 1:
                        company = parts[1].split("\n")[0].strip()

            # Location
            location = "Remote"
            try:
                location_elem = card.find_element(By.CLASS_NAME, "locations")
                loc_text = location_elem.text.strip()
                if loc_text:
                    location = loc_text
            except:
                # Look for location in text
                if "Work From Home" in card_text or "WFH" in card_text:
                    location = "Remote"

            # Build description
            description = f"{title} at {company}. Location: {location}."

            # Try to get additional details
            try:
                meta = card.find_element(By.CLASS_NAME, "internship_meta")
                meta_text = meta.text.strip()
                if meta_text:
                    # Clean and add metadata
                    meta_lines = [line.strip() for line in meta_text.split("\n") if line.strip()]
                    if len(meta_lines) > 0:
                        description += " " + " | ".join(meta_lines[:3])
            except:
                pass

            # Deadline
            deadline = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")

            result = {
                'title': title,
                'description': description,
                'link': link,
                'location': location,
                'company_name': company,
                'deadline': deadline,
                'job_type': 'Internship'
            }

            return result

        except Exception as e:
            print(f"   ⚠️  Extraction error: {str(e)[:100]}")
            return None

    def process_internship(self, internship):
        """Process and insert/update internship"""
        try:
            # Create fingerprint
            url_hash = self.create_fingerprint(internship['link'], internship['title'])

            # Prepare data
            opp_data = {
                'title': internship['title'],
                'description': internship['description'],
                'link': internship['link'],
                'url_hash': url_hash,
                'source': self.source_name,
                'location': internship['location'],
                'deadline': internship['deadline'],
                'company_name': internship['company_name'],
                'job_type': internship['job_type'],
                'skill_ids': self.extract_skills_from_text(internship['description'] + ' ' + internship['title'])
            }

            # Insert or update
            opp_id, status = OpportunityInserter.insert_or_update(opp_data)

            if status == 'added':
                self.stats['added'] += 1
                print(f"   ✅ Added: {internship['title']}")
            elif status == 'updated':
                self.stats['updated'] += 1
                print(f"   🔄 Updated: {internship['title']}")
            elif status == 'duplicate':
                self.stats['duplicate'] += 1
                print(f"   ⏭️  Duplicate: {internship['title']}")
            else:
                self.stats['errors'] += 1

        except Exception as e:
            self.stats['errors'] += 1
            print(f"   ❌ Error processing {internship.get('title', 'Unknown')}: {e}")

    def go_to_next_page(self):
        """Navigate to next page"""
        try:
            # Find next page button
            next_button = self.driver.find_element(By.ID, "navigation-forward")

            if "disabled" in next_button.get_attribute("class"):
                return False

            next_button.click()
            time.sleep(2)
            return True

        except Exception as e:
            print(f"   ⚠️  Could not find next page: {e}")
            return False


def scrape_internshala_live(max_pages=2, categories=None):
    """
    Scrape live data from Internshala

    Args:
        max_pages: Number of pages to scrape per category
        categories: List of categories to scrape
    """
    if categories is None:
        categories = [
            'computer-science',
            'web-development',
            'data-science',
            'python',
            'machine-learning'
        ]

    print("🚀 Starting Internshala live scraper...")
    print(f"📚 Categories: {', '.join(categories)}")
    print(f"📄 Pages per category: {max_pages}\n")

    for category in categories:
        print(f"\n{'=' * 60}")
        print(f"📂 Scraping category: {category}")
        print(f"{'=' * 60}")

        scraper = InternshalaRealScraper()
        try:
            scraper.scrape(max_pages=max_pages, category=category)
        except Exception as e:
            print(f"❌ Error scraping {category}: {e}")

        # Delay between categories
        print("\n⏸️  Waiting 5 seconds before next category...")
        time.sleep(5)

    print("\n" + "=" * 60)
    print("✅ All categories scraped!")
    print("=" * 60)


if __name__ == "__main__":
    # Scrape 2 pages from computer-science category
    scraper = InternshalaRealScraper()
    scraper.scrape(max_pages=2, category='computer-science')