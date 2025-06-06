from top_companies import fetch_top_companies, print_top_companies
from historical_data import fetch_historical_data, print_historical_data
from histogram_data import fetch_histogram_data, print_histogram_data
from get_and_print_jobs import fetch_jobs, print_job_summary

def main():
    roles = [
        "Software Engineer", "Data Scientist",
        "DevOps Engineer", "Data Analyst", "Blockchain Engineer",
        "UX Designer", "Cyber Security Engineer", "Cloud Developer",
    ]

    country_code = "in"  # "in" for India
    location0 = "IN"  # Top-level location for India
    location1 = "Delhi"  # Specific region/state: Delhi
    category = "it-jobs"  # Example category for IT jobs
    app_id = "e25e59be"  # Replace with your actual app_id
    app_key = "6a555566ccfeda8e4dbe3beda4c062f5"  # Replace with your actual app_key

    for role in roles:
        print(f"Fetching trends for {role}...")

        # Job summary
        data = fetch_jobs(role, country_code)
        print_job_summary(data, role)

        ''' Historical data
        hist_data = fetch_historical_data(country_code, location0, location1, category, app_id, app_key)
        print_historical_data(hist_data, location1, category) '''

        # Top companies
        top_companies_data = fetch_top_companies(role, country_code, app_id, app_key)
        print_top_companies(top_companies_data, role)

        ''' Histogram data
        histogram_data = fetch_histogram_data(role, location0, location1, country_code, app_id, app_key)
        print_histogram_data(histogram_data, role) '''

if __name__ == "__main__":
    main()