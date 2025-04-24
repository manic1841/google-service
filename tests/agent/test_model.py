import json

from agent.models import DirectionsModel

def test_direction_model():
    with open("tests/agent/samples/directions_response.json", "r") as f:
        response = json.load(f)

    DirectionsModel.parse_obj(response)
