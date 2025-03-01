import msal
import requests
from bs4 import BeautifulSoup

GRAPH_API_URL = "https://graph.microsoft.com/v1.0"

def skim_email(text):
    soup = BeautifulSoup(text, "html.parser")
    email_text = soup.get_text()
    email_text = email_text.replace("\n", " ")
    email_text = email_text.split("|")[0].split("From: ")[0]
    return email_text


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

    # Fetching emails at the endpoint iteratively until no more emails are left (999 at a time to avoid rate limiting)
    res = {}

    while messages_endpoint:
        response = requests.get(messages_endpoint, headers=headers)
        if response.status_code == 200:
            messages = response.json().get("value", [])
            print(len(messages))

            # Handling the emails one by one
            for i in range(len(messages)):
                try:
                    # filtering out automated emails, unsolicited requests, and other irrelevant emails
                    message = messages[i]
                    if (message == None 
                    or len(message['categories']) == 0 
                    or message['categories'] == ['Automated emails'] 
                    or message['categories'] == ['Unsolicited requests/offers']
                    or "Automatic reply" in message['subject']
                    or message['from']['emailAddress']['address'] == "rrms@surgeifrc.org"
                    or message['from']['emailAddress']['address'] == "go@ifrc.org"
                    or message['from']['emailAddress']['address'] == "GO.Staging@ifrc.org"
                    or message['from']['emailAddress']['address'] == "lars.tangen@ifrc.org"):
                        continue
                    # grouping emails by conversation ID through a dictionary
                    if message["conversationId"] in res:
                        res[message["conversationId"]].append({
                            "subject": message["subject"],
                            "from": message["from"]["emailAddress"]["address"],
                            "receivedDateTime": message["receivedDateTime"],
                            "body": skim_email(message["body"]["content"]),
                            "conversationID": message["conversationId"]
                        })
                    else:
                        res[message["conversationId"]] = [{
                            "subject": message["subject"],
                            "from": message["from"]["emailAddress"]["address"],
                            "receivedDateTime": message["receivedDateTime"],
                            "body": skim_email(message["body"]["content"]),
                            "conversationID": message["conversationId"]
                        }]
                except Exception as e:
                    print("Error:", e)
                    continue
        
        else:
            raise Exception(f"Error fetching emails: {response.status_code} {response.text}")
        messages_endpoint = response.json().get("@odata.nextLink", None)
        if not messages_endpoint:
            print("Reached the last page of messages.")
            break  # Stop if no more pages exist
    # store the filtered emails as a text file
        # to be updated to directly store in a database and perform sentiment analysis in the future
    with open("output.txt", "w") as f:
        for _, val in res.items():
            if len(val) > 1:
                f.write(str(val) + "\n")
        f.close()


# Count total number of emails just in case there is a mismatch
def email_count(access_token, user_id):
    url = f"{GRAPH_API_URL}/users/{user_id}/messages?$count=true"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "ConsistencyLevel": "eventual"  # Required for $count
    }
    response = requests.get(url, headers=headers)
    # Parse response
    total_emails = 0
    if response.status_code == 200:
        data = response.json()
        total_emails = data.get("@odata.count", 0)  # Extract the total count
        print(f"Total number of emails: {total_emails}")
    else:
        print("Error:", response.json())  # Print error details
    return total_emails

if __name__ == "__main__":
    try:
        # read credentials from secret_env.txt
        credentials = read_secrets()

        # collect the access token
        token = get_access_token(credentials)
        print("Access token acquired successfully.")
        user_id = "im@ifrc.org"
        # total_emails = email_count(token, user_id)

        # store all read emails in a text file (for now)
        get_emails(token, user_id)
    except Exception as e:
        print("shinbal")
        print(f"Error: {e}")

