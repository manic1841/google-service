import polyline
import math
import time
import os

from agent.maps import GoogleMapsClient


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


def main():
    folder = "streetview_images"
    if not os.path.exists(folder):
        os.makedirs(folder)

    client = GoogleMapsClient()
    origin = "New York"
    destination = "Los Angeles"
    directions = client.get_directions(origin, destination)

    if not directions.routes:
        print("No routes found.")
        return

    polyline_str = directions.routes[0].overview_polyline.points
    points = polyline.decode(polyline_str)
    print("Total points:", len(points))

    sampled_points = points[::10]  # Sample every 10th point
    print("Sampled points:", len(sampled_points))

    # Ask user for confirmation before proceeding
    print("Do you want to continue? (yes/no)")
    user_input = input().strip().lower()
    if user_input != "yes" or user_input != "y":
        print("Exiting...")
        return

    print("Starting to download street view images...")

    for i in range(len(sampled_points) - 1):
        lat1, lng1 = sampled_points[i]
        lat2, lng2 = sampled_points[i + 1]
        heading = calculate_bearing(lat1, lng1, lat2, lng2)
        image = client.download_streetview_image(lat1, lng1, heading)

        filename = f"streetview_{i:03d}.jpg"
        with open(filename, "wb") as f:
            f.write(image)
        print(f"Downloaded: {filename} Heading: {int(heading)} degrees")

        time.sleep(0.1)


if __name__ == "__main__":
    main()
