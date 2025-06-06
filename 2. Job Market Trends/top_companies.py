import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Function to fetch top companies data
def fetch_top_companies(job_title, country_code, app_id, app_key):
    session = requests.Session()

    # Configure retries with backoff
    retry = Retry(
        total=5,  # Total retry attempts
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)

    # API endpoint and parameters
    url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/top_companies"
    params = {
        "app_id": app_id,  # Pass API ID as a parameter
        "app_key": app_key,  # Pass API key as a parameter
        "what": job_title,  # Job title to filter top companies
        "content-type": "application/json"
    }

    try:
        response = session.get(url, params=params, timeout=15)
        response.raise_for_status()  # Raise an error for bad responses (4XX or 5XX)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching top companies data for {job_title}: {e}")
        return None

# Function to print top companies data
def print_top_companies(data, job_title):
    if not data or 'leaderboard' not in data:
        print(f"No top companies data found for {job_title}")
        return

    print(f"Top Companies for {job_title}:")
    for company in data['leaderboard']:
        name = company.get('canonical_name', 'N/A')
        count = company.get('count', 'N/A')
        avg_salary = company.get('average_salary', 'N/A')
        print(f"Company: {name}, Vacancies: {count}, Average Salary: {avg_salary}")
    print("-" * 40)
