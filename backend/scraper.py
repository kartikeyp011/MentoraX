import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta


def extract_skills_from_text(text):
    """Extract skill keywords from text"""
    skills_keywords = {
        'python': 1, 'java': 2, 'javascript': 3, 'machine learning': 4,
        'deep learning': 5, 'react': 6, 'node.js': 7, 'nodejs': 7,
        'sql': 8, 'data analysis': 9, 'web development': 10,
        'cloud': 11, 'aws': 11, 'devops': 12, 'docker': 12,
        'security': 13, 'ui/ux': 14, 'design': 14, 'communication': 15
    }

    text_lower = text.lower()
    found_skills = []

    for skill, skill_id in skills_keywords.items():
        if skill in text_lower:
            if skill_id not in found_skills:
                found_skills.append(skill_id)

    return found_skills


def scrape_internshala():
    """Scrape internships from Internshala (simplified version)"""
    opportunities = []

    # Note: For a 4-hour project, we'll create realistic sample data
    # In production, you'd need to handle authentication, pagination, etc.

    sample_internships = [
        {
            "title": "Software Development Intern",
            "description": "Work on Python and JavaScript projects. Build web applications using React and Node.js. Learn cloud deployment on AWS.",
            "location": "Bangalore",
            "source": "Internshala",
            "link": "https://internshala.com/internship/detail/software-development-intern",
            "deadline": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
        },
        {
            "title": "Machine Learning Intern",
            "description": "Work on ML models using Python, TensorFlow. Experience with deep learning and data analysis required.",
            "location": "Remote",
            "source": "Internshala",
            "link": "https://internshala.com/internship/detail/machine-learning-intern",
            "deadline": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
        },
        {
            "title": "Frontend Developer Intern",
            "description": "Build responsive web interfaces using React and JavaScript. Knowledge of UI/UX design principles preferred.",
            "location": "Mumbai",
            "source": "Internshala",
            "link": "https://internshala.com/internship/detail/frontend-developer-intern",
            "deadline": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        },
        {
            "title": "Data Analyst Intern",
            "description": "Analyze data using SQL and Python. Create visualizations and reports. Strong communication skills required.",
            "location": "Hyderabad",
            "source": "Internshala",
            "link": "https://internshala.com/internship/detail/data-analyst-intern",
            "deadline": (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d")
        },
        {
            "title": "Full Stack Developer Intern",
            "description": "Work on both frontend (React) and backend (Node.js, Python). Database experience with SQL required.",
            "location": "Pune",
            "source": "Internshala",
            "link": "https://internshala.com/internship/detail/full-stack-developer-intern",
            "deadline": (datetime.now() + timedelta(days=18)).strftime("%Y-%m-%d")
        },
        {
            "title": "DevOps Intern",
            "description": "Learn cloud infrastructure on AWS. Work with Docker, CI/CD pipelines. Basic Python and scripting knowledge needed.",
            "location": "Remote",
            "source": "Internshala",
            "link": "https://internshala.com/internship/detail/devops-intern",
            "deadline": (datetime.now() + timedelta(days=12)).strftime("%Y-%m-%d")
        },
        {
            "title": "AI Research Intern",
            "description": "Research in deep learning and machine learning. Python, TensorFlow experience required. Work on cutting-edge AI projects.",
            "location": "Bangalore",
            "source": "Internshala",
            "link": "https://internshala.com/internship/detail/ai-research-intern",
            "deadline": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        },
        {
            "title": "Backend Developer Intern",
            "description": "Build APIs using Python or Java. Work with SQL databases. Understanding of web development principles.",
            "location": "Delhi",
            "source": "Internshala",
            "link": "https://internshala.com/internship/detail/backend-developer-intern",
            "deadline": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        },
        {
            "title": "Mobile App Developer Intern",
            "description": "Develop mobile apps using React Native or Flutter. JavaScript and UI/UX design skills needed.",
            "location": "Chennai",
            "source": "Internshala",
            "link": "https://internshala.com/internship/detail/mobile-app-developer-intern",
            "deadline": (datetime.now() + timedelta(days=22)).strftime("%Y-%m-%d")
        },
        {
            "title": "Cybersecurity Intern",
            "description": "Learn security best practices. Work on vulnerability assessment. Python scripting and network security knowledge preferred.",
            "location": "Bangalore",
            "source": "Internshala",
            "link": "https://internshala.com/internship/detail/cybersecurity-intern",
            "deadline": (datetime.now() + timedelta(days=16)).strftime("%Y-%m-%d")
        }
    ]

    for internship in sample_internships:
        # Extract skills from description
        skill_ids = extract_skills_from_text(internship['description'])

        opportunities.append({
            "title": internship['title'],
            "description": internship['description'],
            "link": internship['link'],
            "source": internship['source'],
            "location": internship['location'],
            "deadline": internship['deadline'],
            "skill_ids": skill_ids
        })

    return opportunities


def scrape_angellist():
    """Scrape jobs from AngelList (sample data)"""
    opportunities = []

    sample_jobs = [
        {
            "title": "Junior Software Engineer",
            "description": "Join a startup building fintech solutions. Python, JavaScript, React experience. Fast-paced environment.",
            "location": "Bangalore",
            "source": "AngelList",
            "link": "https://angel.co/company/startup/jobs/software-engineer",
            "deadline": (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
        },
        {
            "title": "ML Engineer - Early Career",
            "description": "Build machine learning models for recommendation systems. Python, deep learning, data analysis skills required.",
            "location": "Remote",
            "source": "AngelList",
            "link": "https://angel.co/company/aicompany/jobs/ml-engineer",
            "deadline": (datetime.now() + timedelta(days=40)).strftime("%Y-%m-%d")
        },
        {
            "title": "Frontend Engineer",
            "description": "Create beautiful user interfaces with React and modern JavaScript. UI/UX design collaboration.",
            "location": "Mumbai",
            "source": "AngelList",
            "link": "https://angel.co/company/techstartup/jobs/frontend-engineer",
            "deadline": (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d")
        },
        {
            "title": "Data Engineer",
            "description": "Build data pipelines using Python and SQL. Work with cloud infrastructure on AWS. DevOps knowledge helpful.",
            "location": "Hyderabad",
            "source": "AngelList",
            "link": "https://angel.co/company/datacompany/jobs/data-engineer",
            "deadline": (datetime.now() + timedelta(days=50)).strftime("%Y-%m-%d")
        },
        {
            "title": "Full Stack Engineer",
            "description": "End-to-end development with React, Node.js, and Python. Work on web development projects from conception to deployment.",
            "location": "Bangalore",
            "source": "AngelList",
            "link": "https://angel.co/company/webstartup/jobs/full-stack-engineer",
            "deadline": (datetime.now() + timedelta(days=38)).strftime("%Y-%m-%d")
        }
    ]

    for job in sample_jobs:
        skill_ids = extract_skills_from_text(job['description'])

        opportunities.append({
            "title": job['title'],
            "description": job['description'],
            "link": job['link'],
            "source": job['source'],
            "location": job['location'],
            "deadline": job['deadline'],
            "skill_ids": skill_ids
        })

    return opportunities


def scrape_linkedin_jobs():
    """Scrape jobs from LinkedIn (sample data)"""
    opportunities = []

    sample_jobs = [
        {
            "title": "Software Developer - New Grad",
            "description": "Work with Java and cloud technologies. DevOps practices and CI/CD. Strong communication skills essential.",
            "location": "Pune",
            "source": "LinkedIn",
            "link": "https://linkedin.com/jobs/software-developer-new-grad",
            "deadline": (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d")
        },
        {
            "title": "Data Scientist - Entry Level",
            "description": "Apply machine learning and data analysis techniques. Python, SQL, and statistical modeling. Collaborate with product teams.",
            "location": "Bangalore",
            "source": "LinkedIn",
            "link": "https://linkedin.com/jobs/data-scientist-entry-level",
            "deadline": (datetime.now() + timedelta(days=32)).strftime("%Y-%m-%d")
        },
        {
            "title": "React Developer",
            "description": "Build scalable web applications with React and JavaScript. Modern web development practices. UI/UX collaboration.",
            "location": "Remote",
            "source": "LinkedIn",
            "link": "https://linkedin.com/jobs/react-developer",
            "deadline": (datetime.now() + timedelta(days=26)).strftime("%Y-%m-%d")
        },
        {
            "title": "Cloud Engineer - Graduate",
            "description": "Deploy and manage AWS infrastructure. DevOps tools like Docker. Python or Java scripting.",
            "location": "Chennai",
            "source": "LinkedIn",
            "link": "https://linkedin.com/jobs/cloud-engineer-graduate",
            "deadline": (datetime.now() + timedelta(days=42)).strftime("%Y-%m-%d")
        },
        {
            "title": "Security Analyst",
            "description": "Monitor and protect systems from cybersecurity threats. Python scripting and security tools. Communication with stakeholders.",
            "location": "Delhi",
            "source": "LinkedIn",
            "link": "https://linkedin.com/jobs/security-analyst",
            "deadline": (datetime.now() + timedelta(days=24)).strftime("%Y-%m-%d")
        }
    ]

    for job in sample_jobs:
        skill_ids = extract_skills_from_text(job['description'])

        opportunities.append({
            "title": job['title'],
            "description": job['description'],
            "link": job['link'],
            "source": job['source'],
            "location": job['location'],
            "deadline": job['deadline'],
            "skill_ids": skill_ids
        })

    return opportunities


def scrape_opportunities():
    """Main scraper function"""
    print("🔍 Starting scraper...")

    all_opportunities = []

    # Scrape from multiple sources
    print("📥 Scraping Internshala...")
    all_opportunities.extend(scrape_internshala())

    print("📥 Scraping AngelList...")
    all_opportunities.extend(scrape_angellist())

    print("📥 Scraping LinkedIn...")
    all_opportunities.extend(scrape_linkedin_jobs())

    # Save to JSON
    with open('data/opportunities.json', 'w', encoding='utf-8') as f:
        json.dump(all_opportunities, f, indent=2, ensure_ascii=False)

    print(f"✅ Scraped {len(all_opportunities)} opportunities and saved to data/opportunities.json")

    return all_opportunities


if __name__ == "__main__":
    scrape_opportunities()