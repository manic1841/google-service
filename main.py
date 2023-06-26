#!/usr/bin/env python3
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GoogleAPIClient:
    SECRET_PATH = '.credentials/client_secret.json'
    CREDS_PATH = '.credentials/cred.json'

    def __init__(self, serviceName: str, version: str, scopes: list) -> None:
        self.creds = None
        # The file client_secret.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.CREDS_PATH):
            self.creds = Credentials.from_authorized_user_file(self.CREDS_PATH, scopes)

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.SECRET_PATH, scopes)
                self.creds = flow.run_local_server()
            # Save the credentials for the next run
            with open(self.CREDS_PATH, 'w') as token:
                token.write(self.creds.to_json())

        self.googleAPIService = build(serviceName, version, credentials=self.creds)

if __name__ == '__main__':
    googleSheetAPI = GoogleAPIClient(
        'photoslibrary',
        'v1',
        ['https://www.googleapis.com/auth/photoslibrary.readonly'],
        )

    print(googleSheetAPI.googleAPIService)
