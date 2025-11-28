import requests
from bs4 import BeautifulSoup
import time


class InternshalaScraper:
    def __init__(self):
        self.base_url = "https://internshala.com/internships/"
        self.stats = {
            "added": 0,
            "skipped": 0,
            "failed": 0
        }

    def scrape(self, category="computer-science", max_pages=2):
        print(f"[scrape] Starting Internshala scrape for category='{category}', max_pages={max_pages}")

        for page in range(1, max_pages + 1):
            try:
                url = f"{self.base_url}{category}-internship/"
                if page > 1:
                    url += f"page-{page}/"

                print(f"\n[scrape] Opening {url}")
                response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(response.text, "html.parser")

                cards = soup.select("div.individual_internship")
                print(f"[scrape] Found {len(cards)} internship card(s) on page {page}")

                for idx, card in enumerate(cards, start=1):
                    try:
                        # --- Title ---
                        title_elem = card.select_one("h3.job-internship-name a.job-title-href")
                        title = title_elem.get_text(strip=True) if title_elem else "Not specified Internship"

                        # --- Company ---
                        company_elem = card.select_one("p.company-name")
                        company = company_elem.get_text(strip=True) if company_elem else "Not specified Company"

                        # --- Location ---
                        location_elem = card.select_one(".locations span a")
                        location = location_elem.get_text(strip=True) if location_elem else "Not specified Location"

                        # --- Stipend ---
                        stipend_elem = card.select_one(".stipend")
                        stipend = stipend_elem.get_text(strip=True) if stipend_elem else "Not specified Stipend"

                        # --- Duration ---
                        duration = "Not specified Duration"
                        duration_icon = card.select_one(".ic-16-calendar")
                        if duration_icon:
                            next_span = duration_icon.find_next("span")
                            if next_span:
                                duration = next_span.get_text(strip=True)

                        # --- Description / About job ---
                        desc_elem = card.select_one(".about_job .text")
                        description = desc_elem.get_text(strip=True) if desc_elem else "Not specified Description"

                        # --- Skills ---
                        skills = []
                        skill_elems = card.select(".job_skill")
                        for skill in skill_elems:
                            skills.append(skill.get_text(strip=True))

                        # --- Link ---
                        link = ""
                        if title_elem and title_elem.has_attr("href"):
                            href = title_elem["href"]
                            link = f"https://internshala.com{href}" if href.startswith("/") else href

                        # ============ PRINT EVERYTHING ============
                        print(f"\n--- Internship #{idx} ---")
                        print(f"Title      : {title}")
                        print(f"Company    : {company}")
                        print(f"Location   : {location}")
                        print(f"Stipend    : {stipend}")
                        print(f"Duration   : {duration}")
                        print(f"Link       : {link}")
                        print(f"Description: {description}")
                        print(f"Skills     : {skills}")

                        self.stats["added"] += 1

                    except Exception as e:
                        self.stats["failed"] += 1
                        print(f"[scrape] Exception processing card #{idx} on page {page}: {str(e)}")

                time.sleep(2)

            except Exception as e:
                print(f"[scrape] Unexpected error: {str(e)}")
                self.stats["failed"] += 1

        print("\n==== SCRAPE SUMMARY ====")
        print(f"Added: {self.stats['added']}")
        print(f"Skipped: {self.stats['skipped']}")
        print(f"Failed: {self.stats['failed']}")


if __name__ == "__main__":
    scraper = InternshalaScraper()
    scraper.scrape(category="computer-science", max_pages=1)