#!/usr/bin/env python3
import os
import requests
import typing as t

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError

SRC_FOLDER = os.path.abspath(os.path.join(__file__, "../../.."))

SECRET_PATH = os.path.join(SRC_FOLDER, ".credentials/client_secret.json")
CREDS_PATH = os.path.join(SRC_FOLDER, ".credentials/cred.json")


class HttpClient:
    def _raise_error(self, response: requests.Response, title):
        try:
            body = response.json()
        except requests.exceptions.JSONDecodeError:
            body = {"code": response.status_code, "message": response.text}
        error = body.get("error")
        if error:
            code = error["code"]
            message = error["message"]
        else:
            code = response.status_code
            message = body

        format_str = f"{title}, code: {code}, message: {message}"
        raise RuntimeError(format_str)


class GoogleAPIClient(HttpClient):
    def __init__(self, scopes: list) -> None:
        self.creds = None
        try:
            self.creds = self._load_cred(scopes)
        except RefreshError:
            os.remove(CREDS_PATH)
            self.creds = self._load_cred(scopes)

        if not self.creds:
            raise RuntimeError("Failed to get Google credentials")

        self.authorization = f"Bearer {self.creds.token}"
        self.headers = {"Authorization": self.authorization}
        # self.googleAPIService = build(serviceName, version, credentials=self.creds, static_discovery=False)

    def _load_cred(self, scopes: list):
        creds = None
        # The file client_secret.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(CREDS_PATH):
            creds = Credentials.from_authorized_user_file(CREDS_PATH, scopes)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(SECRET_PATH, scopes)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open(CREDS_PATH, "w") as token:
                token.write(creds.to_json())
        return creds
