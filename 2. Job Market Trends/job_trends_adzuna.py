import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Function to fetch job data with retry mechanism and timeout handling
def fetch_jobs(job_title, country_code):
    session = requests.Session()

    # Configure retries with backoff
    retry = Retry(
        total=5,  # Total retry attempts
        backoff_factor=1,  # Time between retries: 1, 2, 4, 8, etc. seconds
        status_forcelist=[429, 500, 502, 503, 504]  # Retry on these HTTP statuses
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)

    # API endpoint and parameters
    url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
    params = {
        "app_id": "e25e59be",
        "app_key": "9c9211e04d030c34d3c2f8c8e54105e1",
        "title_only": job_title,
        "results_per_page": 100
    }

    try:
        # Fetch job data with a 15-second timeout
        response = session.get(url, params=params, timeout=15)
        response.raise_for_status()  # Raise an error for bad responses (4XX or 5XX)
        return response.json()
    except requests.exceptions.RequestException as e:
        # Log error and return None for failed requests
        print(f"Error fetching data for {job_title}: {e}")
        return None

# Function to print job summary including salary range
def print_job_summary(data, job_title):
    if not data or 'results' not in data:
        print(f"No data found for {job_title}")
        return

    # Extract job details from API response
    try:
        listings = data['count']
        mean_salary = data['mean']
        min_salary = data['results'][0].get('salary_min', 'N/A')
        max_salary = data['results'][0].get('salary_max', 'N/A')
        top_company = data['results'][0].get('company', {}).get('display_name', 'N/A')
        location = data['results'][0].get('location', {}).get('display_name', 'N/A')
        contract_type = data['results'][0].get('contract_type', 'N/A')
    except (IndexError, KeyError):
        print(f"Error parsing job data for {job_title}")
        return

    # Print job summary
    print(f"Job Title: {job_title}")
    print(f"Number of Listings: {listings}")
    print(f"Mean Salary: {mean_salary}")
    print(f"Salary Range: {min_salary} - {max_salary}")
    print(f"Top Company: {top_company}")
    print(f"Location: {location}")
    print(f"Contract Type: {contract_type}")
    print("-" * 40)



# Main function to fetch and display job trends for various roles

