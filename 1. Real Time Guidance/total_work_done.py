# main.py

from serapi_final import get_job_descriptions
from extract_keywords import extract_keywords
from roadmap_creator import create_roadmap
import json


def main():
    role = "Data Scientist"

    # Get job descriptions
    job_details = get_job_descriptions(role, num_jobs=1)

    if job_details:
        job = job_details[0]  # Get the first job description
        description = job['description']

        # Extract keywords
        keywords = extract_keywords(description)

        # Create roadmap
        roadmap = create_roadmap(keywords)

        # Print results
        print("Job Title:", job['title'])
        print("Keywords:", keywords)
        print("Roadmap:", roadmap)
    else:
        print("No job description found.")


if __name__ == "__main__":
    main()