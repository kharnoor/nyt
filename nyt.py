import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request  # Add this line
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the sender's email address and the target folder (label) name
sender_email = "nytdirect@nytimes.com"
folder_name = "nyt"

# Scope required for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def create_service():
    """Creates a Gmail service object using the provided credentials."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

def move_emails(service, user_id, query, label_name):
    """Moves emails from the specified sender to the target folder (label)."""
    try:
        # Get the ID of the target folder (label)
        labels = service.users().labels().list(userId=user_id).execute()
        label_id = None
        for label in labels['labels']:
            if label['name'] == label_name:
                label_id = label['id']
                break

        if not label_id:
            print(f"Folder (label) '{label_name}' not found.")
            return

        # Find the matching messages
        response = service.users().messages().list(userId=user_id, q=query).execute()
        messages = response.get('messages', [])

        if not messages:
            print('No messages found.')
            return

        # Move each message to the target folder (label)
        for message in messages:
            msg_id = message['id']
            move_request = service.users().messages().modify(
                userId=user_id,
                id=msg_id,
                body={'addLabelIds': [label_id], 'removeLabelIds': ['INBOX']}
            ).execute()
            print(f"Moved message: {msg_id}")

    except HttpError as error:
        print(f'An error occurred: {error}')

def main():
    # Create the Gmail service object
    service = create_service()

    # Specify the query to filter messages from the sender
    query = f"from:{sender_email}"

    # Move the emails to the specified folder (label)
    move_emails(service, "me", query, folder_name)

if __name__ == '__main__':
    main()
