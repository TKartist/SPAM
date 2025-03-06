import requests
import os
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GIT_API_KEY")

OWNER = "IFRCGo"
REPO = "go-web-app"

headers = {"Authorization": f"token {GITHUB_TOKEN}"}
url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues"

params = {
    "state": "all",  
    "per_page": 100,
    "page": 1
}
all_issues = []

while True:
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print("Error:", response.status_code, response.json())
        break

    issues = response.json()
    
    if not issues:  # Stop if no more issues are found
        break
    
    all_issues.extend(issues)
    params["page"] += 1  # Move to next page

print(f"Total Issues Fetched: {len(all_issues)}")

for key, val in all_issues[0].items():
    print(f"{key} : {val}")

# # Print issue titles and URLs
# for issue in all_issues:
#     print(f"#{issue['number']} - {issue['title']} ({issue['html_url']})")