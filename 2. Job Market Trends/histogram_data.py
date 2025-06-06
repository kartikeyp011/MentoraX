import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Function to fetch histogram data
def fetch_histogram_data(job_title, location0, location1, country_code, app_id, app_key):
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
    url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/histogram"
    params = {
        "app_id": app_id,  # Pass API ID as a parameter
        "app_key": app_key,  # Pass API key as a parameter
        "what": job_title,  # Job title to filter
        "location0": location0,  # Top-level location for country
        "location1": location1  # Specific region/state
    }

    try:
        response = session.get(url, params=params, timeout=15)
        response.raise_for_status()  # Raise an error for bad responses (4XX or 5XX)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching histogram data for {job_title}: {e}")
        return None

# Function to print histogram data
def print_histogram_data(data, job_title):
    if not data or 'histogram' not in data:
        print(f"No histogram data found for {job_title}")
        return

    print(f"Salary Histogram for {job_title}:")
    for salary_range, vacancies in data['histogram'].items():
        print(f"Salary Range: {salary_range}, Number of Vacancies: {vacancies}")
    print("-" * 40)
