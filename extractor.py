import msal
import requests

GRAPH_API_URL = "https://graph.microsoft.com/v1.0"


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
    
    messages_endpoint = f"{GRAPH_API_URL}/users/{user_id}/messages?top=50"
    
    response = requests.get(messages_endpoint, headers=headers)
    
    if response.status_code == 200:
        messages = response.json().get("value", [])
        print(len(messages))
        for message in messages:
            print(f"Subject: {message.get('subject')}")
            print(f"From: {message.get('from', {}).get('emailAddress', {}).get('address')}")
            print(f"To: {[recipient['emailAddress']['address'] for recipient in message.get('toRecipients', [])]}")
            print(f"Body Preview: {message.get('bodyPreview')}")
            print("="*50)
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

