import requests

from .client import GoogleAPIClient


class GoogleDriverClient(GoogleAPIClient):
    def get_metadata(self, file_id):
        url = f"https://www.googleapis.com/drive/v2/files/{file_id}"
        ret = requests.get(url, headers=self.headers)

        if not ret.ok:
            self._raise_error(ret, "Error occurred when getting file metadata")

        response = ret.json()
        print(response)
