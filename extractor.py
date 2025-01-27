import requests as req
import csv
from msal import ConfidentialClientApplication
from flask import Flask, request, redirect, session, url_for

import pytz
from datetime import datetime, timedelta


app = Flask(__name__)

def save_emails(emails):
    try:
        with open("initial_email_storage.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=emails[0].keys())
            writer.writeheader()
            writer.writerows(emails)
    except Exception as e:
        print(f"Error: {e}")

def read_secrets():
    try:
        with open("secret_env.txt", "r") as f:
            credentials = f.read().splitlines()
            dict = {}
            for cred in credentials:
                dict[cred.split("=")[0]] = cred.split("=")[1]
            return dict
    except FileNotFoundError:
        print("File not found")


def categorize_email(emails):
    print("got here")


@app.route('/')
def index():
    auth_url = msal_app.get_authorization_request_url(
        scopes=["User.Read", "Mail.Read"],
        redirect_uri=redirect_uri
    )
    return redirect(auth_url)


@app.route('/getToken')
def get_a_token():
    code = request.args.get('code')
    if not code:
        return "Error: No authorization code provided."
    
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=["User.Read", "Mail.Read"],
        redirect_uri=redirect_uri
    )
    if "access_token" in result:
        session['access_token'] = result['access_token']
        return redirect(url_for('read_emails'))
    else:
        return f"Error: {result.get('error')}. Description: {result.get('error_description')}"


@app.route('/read_emails')
def read_emails():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('index'))
    url = "https://graph.microsoft.com/v1.0/me/messages?$top=50"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = req.get(url, headers=headers)
    counter = 1
    if response.status_code == 200:
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        emails = response.json()
        email_list = []
        email_parent_folders = []
        cest = pytz.timezone("Europe/Berlin")
        threshold_time = datetime.now(cest) - timedelta(days=1)

        for email in response.json()["value"]:
            received_time = datetime.strptime(email["receivedDateTime"], date_format).replace(tzinfo=pytz.utc).astimezone(cest)
            if received_time > threshold_time:
                break


            email_dict = {
                "subject": email.get("subject").replace('/', '_'),
                "from" : email.get('from', {}).get('emailAddress', {}).get('address'),
                "body": email.get("bodyPreview"),
            }

            email_list.append(email_dict)
        save_emails(email_list)

    else:
        print(f"Error: {response.status_code}")


if __name__ == "__main__":
    creds = read_secrets()
    redirect_uri = 'http://localhost:5000/getToken'

    msal_app = ConfidentialClientApplication(
        creds["client_id"], 
        authority=f"{creds["authority"]}{creds["tenant"]}",
        client_credential=creds["client"],
    )

    app.run(port=5000)
    print("\n")