from agent.maps import GoogleMapsClient

def main():
    direction_client = GoogleMapsClient()
    origin = "25.059859305913076, 121.36310399130835"
    destination = "25.056593672398275, 121.3651196555793"
    directions = direction_client.get_directions(origin, destination)
    print(directions)

if __name__ == "__main__":
    main()
