import pandas as pd
from VARIABLE import ALL_ISSUES, OPEN_ISSUES, CLOSED_ISSUES, ISSUE_COLS, TITLE_PREFIX
import json

def organize_issue():
    df = pd.read_csv(ALL_ISSUES, index_col=False)

    df.loc[:, "created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df[ISSUE_COLS]

    open_issues = df[df["state"] == "open"]
    open_issues = open_issues.sort_values(by="created_at")
    open_issues.to_csv(OPEN_ISSUES)

    closed_issues = df[df["state"] == "closed"]
    closed_issues.to_csv(CLOSED_ISSUES)

def organize_by_user():
    df = pd.read_csv(ALL_ISSUES, index_col=False)
    df.loc[:, "created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df[ISSUE_COLS]

    dfs = {key: sub_df for key, sub_df in df.groupby("user")}

    for key, df in dfs.items():
        df.to_csv(f"../issues_user/{key}.csv", index=False)

