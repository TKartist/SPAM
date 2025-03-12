import requests
from VARIABLE import GITHUB_TOKEN, OWNER, REPO, PARAMS, ALL_ISSUES, BOT
import pandas as pd



all_issues = []


def send_request(params):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues"

    try:
        res = requests.get(url, headers=headers, params=params)

        if res.status_code != 200:
            print("Error:", res.status_code, res.json())
            return []
        
        issues = res.json()
        
        return issues
    except Exception as e:
        print(f"Error found: {e}")
    return []


def extract_login(x):
    assignees = []
    for assignee in x:
        assignees.append(assignee["login"])
    return assignees


def collect_issues():
    params = PARAMS.copy()
    all_issues = []

    while True:
        issues = send_request(params)
        all_issues += issues
        if len(issues) == 0:
            print("\nAll issues collected")
            break
        params["page"] += 1

    df = pd.DataFrame(all_issues)
    filtered_df = df[df["user"].apply(lambda x: x.get("login") != BOT)]
    filtered_df.loc[:, "user"] = filtered_df["user"].apply(lambda x: x.get("login"))
    filtered_df.loc[:, "closed_by"] = filtered_df["closed_by"].apply(lambda x: x.get("login") if pd.notna(x) else None)
    filtered_df.loc[:, "pull_request"] = filtered_df["pull_request"].apply(lambda x: x.get("html_url") if pd.notna(x) else None)
    filtered_df.loc[:, "assignee"] = filtered_df["assignee"].apply(lambda x: x.get("login") if pd.notna(x) else None)
    filtered_df.loc[:, "assignees"] = filtered_df["assignees"].apply(extract_login)
    filtered_df.to_csv(ALL_ISSUES, index=False)

    return filtered_df

collect_issues()