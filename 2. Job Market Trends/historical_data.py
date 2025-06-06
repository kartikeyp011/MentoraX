import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Function to fetch historical job data (salary and vacancy trends)
def fetch_historical_data(country_code, location0, location1, category, app_id, app_key):
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
    url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/history"
    params = {
        "app_id": app_id,  # Pass API ID as a parameter
        "app_key": app_key,  # Pass API key as a parameter
        "location0": location0,  # Example: "IN" for India
        "location1": location1,  # Example: "Delhi" or any other state
        "category": category,  # Example: "it-jobs"
        "content-type": "application/json"
    }

    try:
        response = session.get(url, params=params, timeout=15)
        response.raise_for_status()  # Raise an error for bad responses (4XX or 5XX)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching historical data for {category}: {e}")
        return None

# Function to print historical salary data
def print_historical_data(data, location1, category):
    if not data or 'month' not in data:
        print(f"No historical data found for {category} in {location1}")
        return

    print(f"Historical Salary Data for {category} in {location1}:")
    for month, salary in data['month'].items():
        print(f"{month}: {salary}")
    print("-" * 40)