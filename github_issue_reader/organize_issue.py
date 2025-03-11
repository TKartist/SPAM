import pandas as pd
from VARIABLE import ALL_ISSUES, OPEN_ISSUES, CLOSED_ISSUES, ISSUE_COLS, TITLE_PREFIX


def organize_issue():
    df = pd.read_csv(ALL_ISSUES)
    df = df[~df["body"].str.startswith(TITLE_PREFIX, na=False)]

    df.loc[:, "created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df[ISSUE_COLS]
    print(df["title"])

    open_issues = df[df["state"] == "open"]
    open_issues = open_issues.sort_values(by="created_at")

    open_issues.to_csv(OPEN_ISSUES)

    closed_issues = df[df["state"] == "closed"]
    closed_issues.to_csv(CLOSED_ISSUES)

organize_issue()

