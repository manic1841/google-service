import polyline
import math
import time
import os
import argparse
import typing as t
import csv

from agent.maps import GoogleMapsClient


def get_directions(client: GoogleMapsClient, origin: str, destination: str) -> t.List[t.Tuple[float, float]]:
    """
    Use Google Maps API to get the route between origin and destination.
    However, the route only contains the turn nodes, not the intermediate points.
    So we choose another way to get the route points.
    """
    directions = client.get_directions(origin, destination)

    if not directions.routes:
        print("No routes found.")
        return

    polyline_str = directions.routes[0].overview_polyline.points
    points = polyline.decode(polyline_str)
    return points

def load_route_points(file_path: str) -> t.List[t.Tuple[float, float]]:
    """
    Load route points from a file.
    The file should contain latitude and longitude pairs separated by commas.
    """
    points = []
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            points.append((float(row[0]), float(row[1])))
    return points

def interplate_points(points: t.List[t.Tuple[float, float]], num_points: int) -> t.List[t.Tuple[float, float]]:
    """
    Interpolate points to get a smoother route.
    """
    interpolated_points = []
    for i in range(len(points) - 1):
        lat1, lng1 = points[i]
        lat2, lng2 = points[i + 1]
        for j in range(num_points):
            lat = lat1 + (lat2 - lat1) * j / num_points
            lng = lng1 + (lng2 - lng1) * j / num_points
            interpolated_points.append((lat, lng))
    return interpolated_points

def calculate_bearing(lat1, lon1, lat2, lon2):
    """
    Calculate the bearing between two points on the Earth specified by latitude and longitude.
    """
    d_lon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    x = math.sin(d_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(
        d_lon
    )
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    return (bearing + 360) % 360


def main(args):
    download_folder = "streetview_images"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    client = GoogleMapsClient()
    origin = args.org
    destination = args.dst
    samples = args.sample
    route_file = args.route

    # Get route points
    points = []
    if origin and destination:
        # points = get_directions(client, origin, destination)
        ...
    elif route_file:
        points = load_route_points(route_file)

    if len(points) == 0:
        print("No route points found.")
        return

    points = interplate_points(points, 2)  # Interpolate points to get a smoother route
    print(f"Loaded {len(points)} route points.")

    sampled_points = points[::samples]  # Sample every N points
    print(f"Sampled {len(sampled_points)} points from the route.")

    print('Are you sure you want to download street view images? (y/n)')
    confirm = input().strip().lower()
    if confirm != 'y':
        print("Aborting...")
        return

    print("Starting to download street view images...")

    for i in range(len(sampled_points) - 1):
        lat1, lng1 = sampled_points[i]
        lat2, lng2 = sampled_points[i + 1]
        heading = calculate_bearing(lat1, lng1, lat2, lng2)
        image = client.download_streetview_image(lat1, lng1, heading)

        filename = f"streetview_{i:03d}_{lat1:.5f}_{lng1:.5f}.jpg"
        filepath = os.path.join(download_folder, filename)
        with open(filepath, "wb") as f:
            f.write(image)
        print(f"Downloaded: {filename} Heading: {int(heading)} degrees")

        # Sleep for a while to avoid hitting the API rate limit
        time.sleep(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download street view images along a route."
    )
    parser.add_argument(
        "--org",
        type=str,
        help="Origin location for the route, like 'New York' or '40.7128,-74.0060'",
    )
    parser.add_argument(
        "--dst",
        type=str,
        help="Destination location for the route, like 'Los Angeles' or '34.0522,-118.2437'",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=10,
        help="Sample every N points from the route (default: 10)",
    )
    parser.add_argument(
        "--route",
        type=str,
        default="route_points.csv",
        help="File path to save the route points (default: route_points.csv)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
