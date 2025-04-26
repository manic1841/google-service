#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import csv


def plot_polyline(polyline_points: list):
    # Create a blank 640x480 black image
    image = np.zeros((800, 800, 3), np.uint8)
    # Fill image with gray color(set each pixel to gray)
    image[:] = (128, 128, 128)

    points = np.array(polyline_points, np.float32)

    min_x = min(points[:, 0])
    max_x = max(points[:, 0])
    min_y = min(points[:, 1])
    max_y = max(points[:, 1])
    print(f"min_x: {min_x}, max_x: {max_x}, min_y: {min_y}, max_y: {max_y}")

    ratio = 800 / max(max_x - min_x, max_y - min_y)
    ratio *= 0.8  # 80% of the image size
    x_diff = (800 - (max_x - min_x) * ratio) / 2
    y_diff = (800 - (max_y - min_y) * ratio) / 2

    points = np.array(
        [
            ((y - min_y) * ratio + y_diff, (x - min_x) * ratio + x_diff)
            for x, y in points
        ],
        np.int32,
    )
    points[:, 1] = 800 - points[:, 1]  # flip y-axis
    min_x = min(points[:, 0])
    max_x = max(points[:, 0])
    min_y = min(points[:, 1])
    max_y = max(points[:, 1])
    print(f"min_x: {min_x}, max_x: {max_x}, min_y: {min_y}, max_y: {max_y}")

    red_color = (0, 0, 255)  # BGR
    # cv2.polylines(image, pts=[points], isClosed=True, color=red_color, thickness=3)
    for i in range(len(points) - 1):
        pt1 = points[i]
        pt2 = points[i + 1]
        cv2.line(image, pt1, pt2, red_color, 3)  # BGR

    # draw point
    cv2.circle(image, points[0], 5, (255, 0, 0), -1)  # BGR

    cv2.imshow("Result", image)
    cv2.waitKey(0)


def main():
    polyline_points = [
        (40.71276, -74.00651),
        (40.74781, -74.17133),
        (40.82978, -74.32815),
        (40.8939, -74.48568),
        (40.89217, -74.67387),
    ]

    polyline_points = []
    with open("route_points.csv", "r") as f:
        reader = csv.reader(f)
        # skip first two rows
        for _ in range(2):
            next(reader)
        for row in reader:
            polyline_points.append((float(row[0]), float(row[1])))

    # plot the latitude and longitude points
    plot_polyline(polyline_points)


if __name__ == "__main__":
    main()
