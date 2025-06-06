from get_and_print_jobs import fetch_jobs, print_job_summary

def main():
    roles = [
        "Software Engineer", "Data Scientist", "Product Manager",
        "DevOps Engineer", "Data Analyst", "Blockchain Engineer",
        "UX Designer", "Cyber Security Engineer", "Cloud Developer",
        "Digital Marketing Specialist", "Project Manager"
    ]

    country_code = "in"  # Example: "in" for India

    for role in roles:
        print(f"Fetching trends for {role}...")
        data = fetch_jobs(role, country_code)
        print_job_summary(data, role)

# Run the main function
if __name__ == "__main__":
    main()