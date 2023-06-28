#!/usr/bin/env python3
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SECRET_PATH = '.credentials/client_secret.json'
CREDS_PATH = '.credentials/cred.json'

class GoogleAPIClient:
    def __init__(self, serviceName: str, version: str, scopes: list) -> None:
        self.creds = None
        # The file client_secret.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(CREDS_PATH):
            self.creds = Credentials.from_authorized_user_file(CREDS_PATH, scopes)

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    SECRET_PATH, scopes)
                self.creds = flow.run_local_server()
            # Save the credentials for the next run
            with open(CREDS_PATH, 'w') as token:
                token.write(self.creds.to_json())

        self.googleAPIService = build(serviceName, version, credentials=self.creds)


def create_google_client(service_name: str, version: str, scopes: list):
    creds = None
    if os.path.exists(CREDS_PATH):
        creds = Credentials.from_authorized_user_file(CREDS_PATH, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                SECRET_PATH, scopes
            )
            creds = flow.run_local_server()
        # Save credential for next run
        with open(CREDS_PATH, 'w') as token:
            token.write(creds.to_json())

    service = build(service_name, version, credentials=creds, static_discovery=False)
    return service, creds

