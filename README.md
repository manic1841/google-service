# google-service
Google API examples

## Setup Google Credentials
Create `.credentials/` folder and put your api key in the folder.
```
mkdir .credentials
# put googlde credential
mv <your_client_secret.json> .credentials/client_secret.json
# put map api key, if you want to use google maps api
mv <your_map_api_key.txt> .credentials/map_api_key.txt
```

## Route Scripts
- `download_route_streetview.py`: Download streetview according the route points you provide or the route points from direction API.
- `generate_video.py`: Create a video from a list of images and plot latitude and longitude on the left top.
- `plot_route.py`: Preview the route points.
