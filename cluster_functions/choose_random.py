import pandas as pd
import os

def choose_random_issues(issues, n=10):
    if len(issues) < n:
        raise ValueError("Not enough issues to choose from.")
    
    return issues.sample(n=n, random_state=1)


def main():
    issue_files = os.listdir("../irrelevant_split")
    issue_files = [x.split(".")[0] for x in issue_files if x.endswith(".csv")]
    github = [x for x in issue_files if "github" in x]
    email = [x for x in issue_files if "email" in x]
    git_dfs = [pd.read_csv(f"{os.path.join("../irrelevant_split", x)}.csv") for x in github]
    email_dfs = [pd.read_csv(f"{os.path.join("../irrelevant_split", x)}.csv") for x in email]
    git_df = pd.concat(git_dfs).drop_duplicates(subset='ids')
    email_df = pd.concat(email_dfs).drop_duplicates(subset='ids')
    email_sample = choose_random_issues(email_df, n=10)
    git_sample = choose_random_issues(git_df, n=10)
    email_sample.to_csv("../random_email_issues.csv", index=False)
    git_sample.to_csv("../random_github_issues.csv", index=False)

    print("Random Sampling Complete")


if __name__ == "__main__":
    main()

