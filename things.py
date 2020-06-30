import base64
import os
import pickle
from email.mime.text import MIMEText

import click
from google.auth.transport import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://mail.google.com/']
CLIENT_SECRET = './credentials.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
USER_ID = os.environ.get('USER_ID')
THINGS_MAIL = os.environ.get('THINGS_MAIL')


def get_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
    credentials = flow.run_local_server(host='localhost', port=8080, open_browser=True)
    return credentials

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return { 'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def build_gmail_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = get_credentials()
            # Save credentials
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
    service = build(API_NAME, API_VERSION, credentials=creds)
    return service

@click.command()
@click.option('--task', prompt='What is the next task?')
def todo(task):
    service = build_gmail_service()
    message = create_message(USER_ID, THINGS_MAIL, task, 'Task added using python')
    service.users().messages().send(userId=USER_ID, body=message).execute()
    print('Done')

if __name__ == "__main__":
    click.clear()
    todo()
