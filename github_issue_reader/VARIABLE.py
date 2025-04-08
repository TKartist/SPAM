from dotenv import load_dotenv
import os

load_dotenv()
GITHUB_TOKEN = os.getenv("GIT_API_KEY")

OWNER = "IFRCGo"
REPO = "go-web-app"

PARAMS = {
    "state": "all",  
    "per_page": 100,
    "page": 1
}

ALL_ISSUES = "../issues_folder/all_issues.csv"
OPEN_ISSUES = "../issues_folder/open_issues.csv"
CLOSED_ISSUES = "../issues_folder/closed_issues.csv"

ISSUE_COLS = [
    "id",
    "number",
    "url",
    "title",
    "body",
    "user",
    "state",
    "assignees",
    "created_at",
    "updated_at",
    "closed_at",
    "author_association",
    "pull_request",
    "closed_by"
]
TITLE_PREFIX = "Bumps"
BOT = "dependabot[bot]"
TRANSFORMER_DIRECTORY = "../local_transformer"
TRANSFORMER_DNAME = "local_transformer"
CLUSTER_KEYWORDS = {
    "register/login" : ["login", "register", "signup", "signin", "password", "username", "email", "forgot", "invalid"],
    "search" : ["search", "find", "filter", "sort", "search result", "searchbox", "searchbar", "inaccurate", "results", "similarity", "relevance"],
    "permissions" : ["permissions", "access", "accessibility", "error", "authorise", "403", "forbidden", "permission denied", "accessibility issue", "hide", "display", "visible", "editing"],
    "data issues" : ["blank", "missing", "not clear", "missing data", "incorrect", "wrong data", "field"],
    "notifications" : ["notification", "alert", "reminder", "receiving", "mailbox"],
    "linked content" : ["redirect", "404", "link", "content", "directed", "404-page", "url", "broken", "new link"],
}
CONSINE_THRESHOLD = 0.95