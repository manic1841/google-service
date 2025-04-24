from agent.maps import GoogleMapsClient

def main():
    client = GoogleMapsClient()
    place = client.search_place("Eiffel Tower")
    print(place)

if __name__ == "__main__":
    main()
