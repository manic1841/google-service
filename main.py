#!/usr/bin/env python3
import os
import shutil

from client import GoogleAPIClient

if __name__ == '__main__':
    googleSheetAPI = GoogleAPIClient(
        'photoslibrary',
        'v1',
        ['https://www.googleapis.com/auth/photoslibrary'],
        )

    print(googleSheetAPI.googleAPIService)

