import requests  # Import the requests library to handle HTTP requests
import json  # Import the json library to handle JSON data
import os  # Import the os library to handle environment variables
from datetime import datetime  # Import datetime to handle date and time

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
        url = "https://data.usajobs.gov/api/search"  # Base URL for the USA Jobs API
        headers = {
            "Authorization-Key": api_key,  # API key for authorization
            "User-Agent": "your-email@example.com"  # User agent header
        }
        all_jobs = {category: {"US": [], "Non-US": []} for category in categories}  # Initialize dictionary to store jobs

        # Iterate through each category and its keywords
        for category, keywords in categories.items():
            for keyword in keywords:
                params = {
                    "Keyword": keyword,  # Keyword to search for jobs
                }
                print(f"Sending request to USA Jobs API for keyword: {keyword}...")  # Log the keyword being searched
                response = requests.get(url, headers=headers, params=params)  # Send the GET request to the API
                response.raise_for_status()  # Raise an error for bad status codes
                print("Request successful. Processing response...")  # Log successful request
                jobs = response.json()  # Parse the JSON response
                print(f"Number of jobs fetched for keyword '{keyword}': {len(jobs.get('SearchResult', {}).get('SearchResultItems', []))}")  # Log the number of jobs fetched
                for job in jobs.get('SearchResult', {}).get('SearchResultItems', []):
                    # Check if the job is located in the US or Non-US
                    job_location = "US" if any(loc.get('CountryCode') == "USA" for loc in job['MatchedObjectDescriptor']['PositionLocation']) else "Non-US"
                    all_jobs[category][job_location].append(job)  # Append job to the appropriate category and location

        # Remove duplicate jobs by Position ID
        for category in all_jobs:
            for location in all_jobs[category]:
                unique_jobs = {}
                for job in all_jobs[category][location]:
                    job_id = job['MatchedObjectId']
                    unique_jobs[job_id] = job
                all_jobs[category][location] = list(unique_jobs.values())

        # Save all jobs to jobs.json file
        with open('jobs.json', 'w', encoding='utf-8') as f:
            json.dump(all_jobs, f, indent=2)  # Write JSON data to file
        print("jobs.json file updated successfully.")  # Log successful update

        update_readme(all_jobs)  # Call function to update README

    except requests.RequestException as e:
        print(f"Request error: {e}")  # Log request error
        raise
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")  # Log JSON decode error
        raise
    except Exception as e:
        print(f"An error occurred: {e}")  # Log any other errors
        raise

def update_readme(all_jobs):
    try:
        readme_content = """
# 🖥️ Latest Tech Job Listings

Welcome to the tech job listings page! Here you will find the most recent job opportunities in the tech industry.

## Table of Contents
- [Jobs](#jobs)
- [How to Apply](#how-to-apply)

## Jobs
"""  # Initialize README content

        # Iterate through categories and locations to build the README content
        for category, locations in all_jobs.items():
            for location, jobs in locations.items():
                location_label = "US" if location == "US" else "Non-US"  # Set location label
                readme_content += f"\n### {category} Jobs ({location_label})\n\n"  # Add category and location to README
                readme_content += "| Job Title | Locations | Link |\n"  # Add table headers
                readme_content += "|-----------|-----------|------|\n"  # Add table headers
                for job in jobs:
                    job_title = job['MatchedObjectDescriptor']['PositionTitle']  # Get job title
                    job_url = job['MatchedObjectDescriptor']['PositionURI']  # Get job URL
                    job_locations = job['MatchedObjectDescriptor']['PositionLocation']  # Get job locations
                    # Check if job has multiple locations and set job_locations_str accordingly
                    job_locations_str = "Multiple Locations" if len(job_locations) > 1 else job_locations[0]['LocationName']
                    readme_content += f"| [{job_title}]({job_url}) | {job_locations_str} | [Apply Here]({job_url}) |\n"  # Add job details to table

        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  # Get current time in UTC
        readme_content += f"""
## How to Apply
- Click on the job title link to view more details and apply.
- Ensure your resume and cover letter are updated.

*Last Updated: {current_time} UTC*
"""  # Add how to apply section and last updated time
        print("README content generated successfully.")  # Log successful generation

        # Write README content to README.md file
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)  # Write content to file
        print("README.md file updated successfully.")  # Log successful update
    except KeyError as e:
        print(f"Key error: {e}")  # Log key error
        raise
    except Exception as e:
        print(f"An error occurred while updating the README: {e}")  # Log any other errors
        raise

if __name__ == "__main__":
    api_key = os.getenv("USAJOBS_API_KEY")  # Get API key from environment variables
    if not api_key:
        print("API key is not set")  # Log if API key is not set
        exit(1)  # Exit if API key is not set
    fetch_jobs(api_key)  # Call function to fetch jobs
