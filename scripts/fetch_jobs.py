import requests
import json
import os
from datetime import datetime

# Define job categories and their keywords
categories = {
    "IT": ["IT", "information technology", "software", "developer", "programmer", "data", "system", "network"],
    "Cybersecurity": ["cybersecurity", "security", "information security"],
    "Engineering": ["engineering", "engineer", "mechanical", "electrical", "civil", "chemical"],
    "Data Science": ["data science", "data scientist", "machine learning", "AI", "artificial intelligence"],
    "Web Development": ["web development", "web developer", "frontend", "backend", "fullstack"],
    "Cloud Computing": ["cloud", "AWS", "Azure", "GCP", "cloud engineer"]
}

def fetch_jobs(api_key):
    try:
        url = "https://data.usajobs.gov/api/search"
        headers = {
            "Authorization-Key": api_key,
            "User-Agent": "your-email@example.com"
        }
        all_jobs = {category: {"US": {"Internships": [], "Jobs": []}, "Non-US": {"Internships": [], "Jobs": []}} for category in categories}

        for category, keywords in categories.items():
            for keyword in keywords:
                params = {
                    "Keyword": keyword,
                    "LocationName": "United States"
                }
                print(f"Sending request to USA Jobs API for keyword: {keyword}...")
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()  # Raise an error for bad status codes
                print("Request successful. Processing response...")
                jobs = response.json()
                print(f"Number of jobs fetched for keyword '{keyword}': {len(jobs.get('SearchResult', {}).get('SearchResultItems', []))}")
                for job in jobs.get('SearchResult', {}).get('SearchResultItems', []):
                    job_location = "US" if any(loc.get('CountryCode') == "USA" for loc in job['MatchedObjectDescriptor']['PositionLocation']) else "Non-US"
                    job_type = "Internships" if "intern" in job['MatchedObjectDescriptor']['PositionTitle'].lower() else "Jobs"
                    all_jobs[category][job_location][job_type].append(job)

        # Remove duplicate jobs by Position ID
        for category in all_jobs:
            for location in all_jobs[category]:
                for job_type in all_jobs[category][location]:
                    all_jobs[category][location][job_type] = list({job['MatchedObjectId']: job for job in all_jobs[category][location][job_type]}.values())

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
# 🖥️ Latest Tech Job Listings

Welcome to the tech job listings page! Here you will find the most recent internships and job opportunities in the tech industry.

## Table of Contents
- [Internships](#internships)
- [Jobs](#jobs)
- [How to Apply](#how-to-apply)

## Internships
"""

        for category, locations in all_jobs.items():
            for location, job_types in locations.items():
                location_label = "US" if location == "US" else "Non-US"
                readme_content += f"\n### {category} Internships ({location_label})\n\n"
                readme_content += "| Job Title | Locations | Link |\n"
                readme_content += "|-----------|-----------|------|\n"
                for job in job_types['Internships']:
                    job_title = job['MatchedObjectDescriptor']['PositionTitle']
                    job_url = job['MatchedObjectDescriptor']['PositionURI']
                    job_locations = job['MatchedObjectDescriptor'].get('PositionLocationDisplay', 'N/A')
                    if isinstance(job_locations, str):
                        job_locations = [job_locations]
                    job_locations = ", ".join(job_locations)
                    readme_content += f"| [{job_title}]({job_url}) | {job_locations} | [Apply Here]({job_url}) |\n"

        readme_content += "\n## Jobs\n"

        for category, locations in all_jobs.items():
            for location, job_types in locations.items():
                location_label = "US" if location == "US" else "Non-US"
                readme_content += f"\n### {category} Jobs ({location_label})\n\n"
                readme_content += "| Job Title | Locations | Link |\n"
                readme_content += "|-----------|-----------|------|\n"
                for job in job_types['Jobs']:
                    job_title = job['MatchedObjectDescriptor']['PositionTitle']
                    job_url = job['MatchedObjectDescriptor']['PositionURI']
                    job_locations = job['MatchedObjectDescriptor'].get('PositionLocationDisplay', 'N/A')
                    if isinstance(job_locations, str):
                        job_locations = [job_locations]
                    job_locations = ", ".join(job_locations)
                    readme_content += f"| [{job_title}]({job_url}) | {job_locations} | [Apply Here]({job_url}) |\n"

        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        readme_content += f"""
## How to Apply
- Click on the job title link to view more details and apply.
- Ensure your resume and cover letter are updated.

*Last Updated: {current_time} UTC*

![Tech Jobs](https://via.placeholder.com/728x90.png)
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
