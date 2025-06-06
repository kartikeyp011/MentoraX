# serapi_final.py

from serpapi import GoogleSearch

def get_job_descriptions(role, location="India", num_jobs=5):
    params = {
        "engine": "google_jobs",
        "q": role,  # Role like Data Scientist, Web Developer, etc.
        "location": location,
        "num": num_jobs,
        "api_key": "YOUR_SERPAPI_KEY"  # Replace with your SerpApi key
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

# Example usage (optional, for testing):
if __name__ == "__main__":
    role = "Data Scientist"
    job_details = get_job_descriptions(role, num_jobs=5)

    # Print all the job details
    for i, job in enumerate(job_details, 1):
        print(f"Job {i} Title: {job['title']}\nDescription:\n{job['description']}\n")
