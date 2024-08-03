import requests
import json
import os
from datetime import datetime

# Define job categories and their keywords
categories = {
    "IT": ["IT", "information technology", "software", "developer", "programming", "database", "systems analyst", "network", "IT support"],
    "Cybersecurity": ["cybersecurity", "security", "information security", "infosec", "cyber defense", "penetration testing", "ethical hacking", "network security", "incident response"],
    "Engineering": ["engineering", "engineer", "mechanical engineering", "electrical engineering", "civil engineering", "chemical engineering", "aerospace engineering", "biomedical engineering", "industrial engineering", "manufacturing engineering"],
    "Data Science": ["data science", "data scientist", "machine learning", "AI", "artificial intelligence", "deep learning", "big data", "data analytics", "data mining", "statistical analysis"],
    "Web Development": ["web development", "web developer", "frontend development", "backend development", "fullstack development", "web design", "UI/UX", "HTML", "CSS", "JavaScript", "React", "Angular", "Vue.js", "Node.js"],
    "Cloud Computing": ["cloud computing", "AWS", "Azure", "GCP", "cloud engineer", "cloud architecture", "cloud services", "cloud infrastructure", "cloud security"],
    "Internships": ["internship", "intern", "co-op", "trainee", "apprenticeship", "summer internship", "graduate internship"]
}


def fetch_jobs(api_key):
    try:
        url = "https://data.usajobs.gov/api/search"
        headers = {
            "Authorization-Key": api_key,
            "User-Agent": "your-email@example.com"
        }
        all_jobs = {category: [] for category in categories}  # Only store jobs, no distinction for US or Non-US

        for category, keywords in categories.items():
            for keyword in keywords:
                params = {
                    "Keyword": keyword
                }
                print(f"Sending request to USA Jobs API for keyword: {keyword}...")
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()  # Raise an error for bad status codes
                print("Request successful. Processing response...")
                jobs = response.json()
                print(f"Number of jobs fetched for keyword '{keyword}': {len(jobs.get('SearchResult', {}).get('SearchResultItems', []))}")
                for job in jobs.get('SearchResult', {}).get('SearchResultItems', []):
                    all_jobs[category].append(job)

        # Remove duplicate jobs by Position ID
        for category in all_jobs:
            all_jobs[category] = list({job['MatchedObjectId']: job for job in all_jobs[category]}.values())

        with open('jobs.json', 'w', encoding='utf-8') as f:
            json.dump(all_jobs, f, indent=2)
        print("jobs.json file updated successfully.")

        update_readme(all_jobs)

    except requests.RequestException as e:
        print(f"Request error: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def update_readme(all_jobs):
    try:
        readme_content = """
# 🖥️ USAJobs: IT, Cybersecurity, Data Science, etc.

Welcome to the USAJobs listings page! Here you will find the most recent federal government tech jobs + Internships.

## Table of Contents
"""
        for category in categories:
             # Replace spaces with hyphens and convert to lowercase for the link
            category_link = category.replace(" ", "-").lower()  # Change implemented here -- added
            readme_content += f"- [{category} Jobs](#{category_link}-jobs)\n"
        readme_content += "\n"

        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        for category, jobs in all_jobs.items():       
            category_link = category.replace(" ", "-").lower() #added
            readme_content += f"## {category} Jobs\n\n"
            readme_content += "| Job Title | Location | Apply By | Link |\n"
            readme_content += "|-----------|----------|----------|------|\n"
            for job in jobs:
                job_title = job['MatchedObjectDescriptor']['PositionTitle']
                job_url = job['MatchedObjectDescriptor']['PositionURI']
                position_location_display = job['MatchedObjectDescriptor']['PositionLocationDisplay']
                apply_by = job['MatchedObjectDescriptor']['ApplicationCloseDate'].split("T")[0]  # Include only date, not time

                if isinstance(position_location_display, list):
                    job_location = ", ".join([loc['LocationName'] for loc in position_location_display])
                else:
                    job_location = position_location_display

                readme_content += f"| [{job_title}]({job_url}) | {job_location} | {apply_by} | [Apply Here]({job_url}) |\n"

            readme_content += "\n"

        readme_content += f"""
## How to Apply
- Click on the job title link to view more details and apply.
- Ensure your resume and cover letter are updated.

*Last Updated: {current_time} UTC*

"""
        print("README content generated successfully.")

        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("README.md file updated successfully.")
    except KeyError as e:
        print(f"Key error: {e}")
        raise
    except Exception as e:
        print(f"An error occurred while updating the README: {e}")
        raise

if __name__ == "__main__":
    api_key = os.getenv("USAJOBS_API_KEY")
    if not api_key:
        print("API key is not set")
        exit(1)
    fetch_jobs(api_key)
