from serpapi import GoogleSearch

def get_job_descriptions(role, location="India", num_jobs=100):
    params = {
        "engine": "google_jobs",
        "q": role,  # Role like Data Scientist, Web Developer, etc.
        "location": location,
        "num": num_jobs,
        "api_key": "***REMOVED***"  # Replace with your SerpApi key
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    jobs = results.get("jobs_results", [])
    job_details = []

    for job in jobs:
        # Get both title and description for each job
        title = job.get("title")
        description = job.get("description")
        if title and description:
            job_details.append({"title": title, "description": description})

    return job_details

# Example usage
role = "Data Scientist"
job_details = get_job_descriptions(role, num_jobs=100)

# Print all the job details
for i, job in enumerate(job_details, 1):
    print(f"Job {i} Title: {job['title']}\nDescription:\n{job['description']}\n")
