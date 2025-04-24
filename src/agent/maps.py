import requests
import os

from agent.client import HttpClient
from agent.models import DirectionsModel


SRC_FOLDER = os.path.abspath(os.path.join(__file__, "../../.."))
MAP_API_KEY_PATH = os.path.join(SRC_FOLDER, ".credentials/map_api_key.txt")

class GoogleMapsClient(HttpClient):
    def __init__(self):
        with open(MAP_API_KEY_PATH, "r") as f:
            self.api_key = f.read().strip()

    def get_directions(self, origin: str, destination: str) -> DirectionsModel:
        """
        Get directions from origin to destination using Google Maps API.
        """
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "key": self.api_key,
        }
        ret = requests.get(url, params=params)

        if not ret.ok:
            self._raise_error(ret, "Error occurred when getting directions")

        return DirectionsModel.parse_obj(ret.json())

    def search_place(self, query: str) -> dict:
        """
        Search for a place using text query.
        """
        url = "https://places.googleapis.com/v1/places:searchText"
        params = {
            "textQuery": query
        }
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress"
        }
        ret = requests.post(url, headers=headers, params=params)

        if not ret.ok:
            self._raise_error(ret, "Error occurred when getting place details")

        return ret.json()

    def download_streetview_image(self, lat: float, lng: float, heading: float) -> bytes:
        """
        Download a street view image from Google Maps API.
        """
        url = "https://maps.googleapis.com/maps/api/streetview"
        params = {
            "size": "640x400",
            "location": f"{lat},{lng}",
            "fov": 90,
            "heading": heading,
            "pitch": 0,
            "key": self.api_key,
        }
        ret = requests.get(url, params=params)

        if not ret.ok:
            self._raise_error(ret, "Error occurred when downloading street view image")

        return ret.content