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