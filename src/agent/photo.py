#!/usr/bin/env python3
import requests
import typing as t
import io

from .models import AlbumModel, MediaItemModel
from .client import GoogleAPIClient


class GooglePhotoClient(GoogleAPIClient):
    def list_all_albums(self) -> t.List[AlbumModel]:
        url = "https://photoslibrary.googleapis.com/v1/albums"
        ret = requests.get(url, headers=self.headers)
        if not ret.ok:
            self._raise_error(ret, "Error occurred when list albums")

        response = ret.json()
        albums_list = []

        for album in response["albums"]:
            albums_list.append(AlbumModel.parse_obj(album))

        next_page_token = response.get("nextPageToken")
        while next_page_token:
            params = {"pageToken": next_page_token}
            ret = requests.get(url, headers=self.headers, params=params)
            if not ret.ok:
                self._raise_error(ret, "Error occurred when list the next albums")
            response = ret.json()
            for album in response["albums"]:
                albums_list.append(AlbumModel.parse_obj(album))

            next_page_token = response.get("nextPageToken")

        return albums_list

    def list_photo_in_albums(self, album: AlbumModel) -> t.List[MediaItemModel]:
        """
        https://photoslibrary.googleapis.com/v1/mediaItems:search
        payload:
        {
           "albumId": string,
            "pageSize": integer,
            "pageToken": string,
            "filters": {
                object (Filters)
            },
            "orderBy": string
        }
        """
        url = "https://photoslibrary.googleapis.com/v1/mediaItems:search"
        payload = {"albumId": album.id}
        ret = requests.post(url, headers=self.headers, json=payload)

        if not ret.ok:
            self._raise_error(
                ret, f"Error occurred when search photos from {album.title}"
            )

        response = ret.json()
        photo_list = []

        for photo in response["mediaItems"]:
            photo_list.append(MediaItemModel.parse_obj(photo))

        next_page_token = response.get("nextPageToken")
        while next_page_token:
            next_payload = payload
            next_payload["pageToken"] = next_page_token
            ret = requests.post(url, headers=self.headers, json=next_payload)

            if not ret.ok:
                self._raise_error(
                    ret, f"Error occurred when search photos from {album.title}"
                )

            response = ret.json()
            for photo in response["mediaItems"]:
                photo_list.append(MediaItemModel.parse_obj(photo))
            next_page_token = response.get("nextPageToken")

        return photo_list

    def download_photo(self, fd: io.BufferedWriter, photo_id=None, baseUrl=None):
        if not baseUrl:
            url = f"https://photoslibrary.googleapis.com/v1/mediaItems/{photo_id}"
            ret = requests.get(url, headers=self.headers)

            if not ret.ok:
                self._raise_error(
                    ret, f"Error occurred when getting photo of {photo_id}"
                )

            response = ret.json()

            photo = MediaItemModel.parse_obj(response)
            baseUrl = photo.baseUrl

        photo_url = baseUrl + "=d"
        ret = requests.get(photo_url)

        if not ret.ok:
            self._raise_error(ret, f"Failed to download photo from {photo_url}")

        fd.write(ret.content)
