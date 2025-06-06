# total_work_done.py

from serapi_final import get_job_descriptions
from extract_keywords import extract_keywords
from roadmap_creator import create_roadmap
import json

def main():
    role = "Data Scientist"

    # Get job descriptions
    job_details = get_job_descriptions(role, num_jobs=5)  # Fetch multiple jobs for better keyword extraction

    if job_details:
        # Extract keywords from each job description
        all_keywords = []
        for job in job_details:
            description = job['description']
            keywords = extract_keywords(description)
            all_keywords.append(keywords)

        # Create roadmap
        roadmap = create_roadmap(all_keywords)

        # Print results
        print("Roadmap:")
        for step in roadmap:
            print(f"- {step.get('skill', 'Unknown Skill')}: Priority {step.get('priority', 'N/A')}, Level {step.get('required_level', 'N/A')}")
    else:
        print("No job description found.")

if __name__ == "__main__":
    main()
