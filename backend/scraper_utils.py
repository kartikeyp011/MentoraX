import hashlib
import time
import random
from datetime import datetime, timedelta
from backend.database import fetch_one, execute_query, fetch_all
import requests
from bs4 import BeautifulSoup


class ScraperBase:
    """Base class for all scrapers with common utilities"""

    def __init__(self, source_name):
        self.source_name = source_name
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        self.session = requests.Session()
        self.stats = {
            'found': 0,
            'added': 0,
            'updated': 0,
            'duplicate': 0,
            'errors': 0
        }

    def get_random_user_agent(self):
        """Return a random user agent"""
        return random.choice(self.user_agents)

    def create_fingerprint(self, url, title):
        """Create unique fingerprint from URL and title"""
        # Normalize URL (remove query params for some cases)
        normalized_url = url.split('?')[0].strip().lower()
        normalized_title = title.strip().lower()

        # Create hash
        fingerprint_string = f"{normalized_url}|{normalized_title}"
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()

    def check_duplicate(self, url_hash, table='opportunities'):
        """Check if item already exists in database"""
        query = f"SELECT * FROM {table} WHERE url_hash = %s"
        result = fetch_one(query, (url_hash,))
        return result

    def random_delay(self, min_seconds=1, max_seconds=3):
        """Add random delay to avoid rate limiting"""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def fetch_page(self, url, retries=3):
        """Fetch page with retries and error handling"""
        for attempt in range(retries):
            try:
                headers = {
                    'User-Agent': self.get_random_user_agent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }

                response = self.session.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    # Rate limited, wait longer
                    print(f"⚠️  Rate limited, waiting {(attempt + 1) * 5} seconds...")
                    time.sleep((attempt + 1) * 5)
                else:
                    print(f"⚠️  Status {response.status_code}, attempt {attempt + 1}/{retries}")

            except requests.exceptions.RequestException as e:
                print(f"❌ Request error: {e}, attempt {attempt + 1}/{retries}")
                if attempt < retries - 1:
                    time.sleep(2)

        return None

    def parse_html(self, response):
        """Parse HTML response"""
        return BeautifulSoup(response.content, 'html.parser')

    def log_scraping(self, scrape_type, status='success', error_message=None):
        """Log scraping activity"""
        try:
            query = """
                    INSERT INTO scraping_logs
                    (source, scrape_type, items_found, items_added, items_updated,
                     items_duplicate, status, error_message, started_at, completed_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                    """
            execute_query(query, (
                self.source_name,
                scrape_type,
                self.stats['found'],
                self.stats['added'],
                self.stats['updated'],
                self.stats['duplicate'],
                status,
                error_message,
                datetime.now() - timedelta(seconds=60),  # Approximate start
                datetime.now()
            ))
        except Exception as e:
            print(f"Error logging scraping activity: {e}")

    def extract_skills_from_text(self, text):
        """Extract skill IDs from text description"""
        skills_keywords = {
            'python': 1, 'java': 2, 'javascript': 3, 'machine learning': 4,
            'deep learning': 5, 'react': 6, 'node.js': 7, 'nodejs': 7,
            'sql': 8, 'data analysis': 9, 'web development': 10,
            'cloud': 11, 'aws': 11, 'devops': 12, 'docker': 12,
            'security': 13, 'ui/ux': 14, 'design': 14, 'communication': 15
        }

        text_lower = text.lower()
        found_skills = []

        for skill, skill_id in skills_keywords.items():
            if skill in text_lower and skill_id not in found_skills:
                found_skills.append(skill_id)

        return found_skills

    def print_stats(self):
        """Print scraping statistics"""
        print(f"\n📊 Scraping Statistics for {self.source_name}:")
        print(f"   Found: {self.stats['found']}")
        print(f"   Added: {self.stats['added']}")
        print(f"   Updated: {self.stats['updated']}")
        print(f"   Duplicates: {self.stats['duplicate']}")
        print(f"   Errors: {self.stats['errors']}")


class OpportunityInserter:
    """Helper class to insert/update opportunities"""

    @staticmethod
    def insert_or_update(opportunity_data):
        """Insert new opportunity or update existing"""
        try:
            # Check if exists
            existing = fetch_one(
                "SELECT opportunity_id, title, description FROM opportunities WHERE url_hash = %s",
                (opportunity_data['url_hash'],)
            )

            if existing:
                # Check if content changed
                if (existing['title'] != opportunity_data['title'] or
                        existing['description'] != opportunity_data['description']):
                    # Update
                    query = """
                            UPDATE opportunities
                            SET title=%s, \
                                description=%s, \
                                location=%s, \
                                deadline=%s,
                                company_name=%s, \
                                job_type=%s, \
                                last_updated=NOW(), \
                                is_active= TRUE
                            WHERE opportunity_id = %s \
                            """
                    execute_query(query, (
                        opportunity_data['title'],
                        opportunity_data['description'],
                        opportunity_data.get('location'),
                        opportunity_data.get('deadline'),
                        opportunity_data.get('company_name'),
                        opportunity_data.get('job_type'),
                        existing['opportunity_id']
                    ))
                    return existing['opportunity_id'], 'updated'
                else:
                    # Mark as active (in case it was inactive)
                    execute_query(
                        "UPDATE opportunities SET is_active=TRUE, last_updated=NOW() WHERE opportunity_id=%s",
                        (existing['opportunity_id'],)
                    )
                    return existing['opportunity_id'], 'duplicate'
            else:
                # Insert new
                query = """
                        INSERT INTO opportunities
                        (title, description, link, url_hash, source, location, deadline,
                         company_name, job_type, scraped_at, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), TRUE) \
                        """
                opp_id = execute_query(query, (
                    opportunity_data['title'],
                    opportunity_data['description'],
                    opportunity_data['link'],
                    opportunity_data['url_hash'],
                    opportunity_data['source'],
                    opportunity_data.get('location'),
                    opportunity_data.get('deadline'),
                    opportunity_data.get('company_name'),
                    opportunity_data.get('job_type')
                ))

                # Insert skills
                if 'skill_ids' in opportunity_data and opportunity_data['skill_ids']:
                    for skill_id in opportunity_data['skill_ids']:
                        try:
                            execute_query(
                                "INSERT IGNORE INTO opportunity_skills (opportunity_id, skill_id) VALUES (%s, %s)",
                                (opp_id, skill_id)
                            )
                        except:
                            pass

                return opp_id, 'added'

        except Exception as e:
            print(f"Error inserting/updating opportunity: {e}")
            return None, 'error'


class CourseInserter:
    """Helper class to insert/update courses"""

    @staticmethod
    def insert_or_update(course_data):
        """Insert new course or update existing"""
        try:
            # Check if exists
            existing = fetch_one(
                "SELECT course_id FROM courses WHERE url_hash = %s",
                (course_data['url_hash'],)
            )

            if existing:
                # Update
                query = """
                        UPDATE courses
                        SET title=%s, \
                            description=%s, \
                            price_type=%s, \
                            price=%s,
                            rating=%s, \
                            last_updated=NOW(), \
                            is_active= TRUE
                        WHERE course_id = %s \
                        """
                execute_query(query, (
                    course_data['title'],
                    course_data['description'],
                    course_data.get('price_type', 'free'),
                    course_data.get('price', 0),
                    course_data.get('rating'),
                    existing['course_id']
                ))
                return existing['course_id'], 'updated'
            else:
                # Insert new
                query = """
                        INSERT INTO courses
                        (title, description, url, url_hash, provider, price_type, price,
                         currency, duration, rating, thumbnail_url, level, scraped_at, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), TRUE) \
                        """
                course_id = execute_query(query, (
                    course_data['title'],
                    course_data['description'],
                    course_data['url'],
                    course_data['url_hash'],
                    course_data['provider'],
                    course_data.get('price_type', 'free'),
                    course_data.get('price', 0),
                    course_data.get('currency', 'USD'),
                    course_data.get('duration'),
                    course_data.get('rating'),
                    course_data.get('thumbnail_url'),
                    course_data.get('level', 'beginner')
                ))

                # Insert skills
                if 'skill_ids' in course_data and course_data['skill_ids']:
                    for skill_id in course_data['skill_ids']:
                        try:
                            execute_query(
                                "INSERT IGNORE INTO course_skills (course_id, skill_id) VALUES (%s, %s)",
                                (course_id, skill_id)
                            )
                        except:
                            pass

                return course_id, 'added'

        except Exception as e:
            print(f"Error inserting/updating course: {e}")
            return None, 'error'


def cleanup_old_opportunities(days=30):
    """Mark opportunities older than X days as inactive"""
    try:
        query = """
                UPDATE opportunities
                SET is_active = FALSE
                WHERE last_updated < DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND is_active = TRUE \
                """
        execute_query(query, (days,))
        print(f"✅ Cleaned up opportunities older than {days} days")
    except Exception as e:
        print(f"Error cleaning up old opportunities: {e}")


def cleanup_old_courses(days=90):
    """Mark courses older than X days as inactive"""
    try:
        query = """
                UPDATE courses
                SET is_active = FALSE
                WHERE last_updated < DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND is_active = TRUE \
                """
        execute_query(query, (days,))
        print(f"✅ Cleaned up courses older than {days} days")
    except Exception as e:
        print(f"Error cleaning up old courses: {e}")