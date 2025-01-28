import msal
import requests
from bs4 import BeautifulSoup

GRAPH_API_URL = "https://graph.microsoft.com/v1.0"

def skim_email(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()


def read_secrets():
    try:
        dict = {}
        with open("secret_env.txt", "r") as f:
            credentials = f.read().splitlines()
            for cred in credentials:
                dict[cred.split("=")[0]] = cred.split("=")[1]
            dict["scopes"] = ["https://graph.microsoft.com/.default"]
            dict["authority"] = f"https://login.microsoftonline.com/{dict['tenant']}"
        return dict        
    except FileNotFoundError:
        print("File not found")

def get_access_token(credentials):
    app = msal.ConfidentialClientApplication(
        credentials["client"],
        authority=credentials["authority"],
        client_credential=credentials["secret"]
    )
    
    result = app.acquire_token_for_client(scopes=credentials["scopes"])
    
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"Unable to get token: {result.get('error_description', result)}")

def get_emails(access_token, user_id):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    messages_endpoint = f"{GRAPH_API_URL}/users/{user_id}/messages?top=999" # top=50 means we are fetching the top 50 emails, it is capped at 999
    response = requests.get(messages_endpoint, headers=headers)
    
    if response.status_code == 200:
        messages = response.json().get("value", [])
        res = []
        counter = 0
        for message in messages:
            if (len(message['categories']) == 0 
            or message['categories'] == ['Automated emails'] 
            or message['categories'] == ['Unsolicited requests/offers'] 
            or message['from']['emailAddress']['address'] == "rrms@surgeifrc.org"
            or message['from']['emailAddress']['address'] == "go@ifrc.org"
            or message['from']['emailAddress']['address'] == "GO.Staging@ifrc.org"
            or message['from']['emailAddress']['address'] == "lars.tangen@ifrc.org"
            or message['from']['emailAddress']['address'] == "IM@ifrc.org"):
                counter += 1
                continue
            print(message["categories"])

            res.append({
                "subject": message["subject"],
                "from": message["from"]["emailAddress"]["address"],
                "receivedDateTime": message["receivedDateTime"],
                "body": skim_email(message["body"]["content"])
            })
        with open("output.txt", "w") as f:
            f.write(str(res))
        f.close()
        print(counter)
    else:
        raise Exception(f"Error fetching emails: {response.status_code} {response.text}")

if __name__ == "__main__":
    try:
        credentials = read_secrets()
        token = get_access_token(credentials)
        print("Access token acquired successfully.")
        
        user_id = "im@ifrc.org"
        get_emails(token, user_id)
    except Exception as e:
        print(f"Error: {e}")

