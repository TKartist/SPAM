import requests as req
import msal


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
    GRAPH_API_URL = "https://graph.microsoft.com/v1.0"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    messages_endpoint = f"{GRAPH_API_URL}/users/{user_id}/messages?%24top=999&%24skip=999"
    while messages_endpoint:
        response = req.get(messages_endpoint, headers=headers)
        if response.status_code == 200:
            messages = response.json().get("value", [])
            print(len(messages))
            messages_endpoint = response.json().get("@odata.nextLink", None)
        else:
            print(response.text)
            break
        print(messages_endpoint)

if __name__ == "__main__":
    creds = read_secrets()
    access_token = get_access_token(creds)
    get_emails(access_token, "im@ifrc.org")
    