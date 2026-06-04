import pytest
from architect import validate_scenario, clean_json_response

def test_clean_json_response():
    raw_md = "```json\n{\"test\": 123}\n```"
    assert clean_json_response(raw_md) == '{"test": 123}'

    raw_plain = '{"test": 123}'
    assert clean_json_response(raw_plain) == '{"test": 123}'

def test_validate_scenario_valid():
    valid_scenario = {
        "title": "Test Game",
        "description": "A test game",
        "starting_room": "room1",
        "rooms": [
            {
                "id": "room1",
                "name": "Start",
                "description": "The beginning.",
                "items": [{"id": "key1", "name": "Key"}],
                "exits": {"north": "room2"}
            },
            {
                "id": "room2",
                "name": "End",
                "description": "The end.",
                "exits": {
                    "south": {
                        "target_room": "room1",
                        "locked": True,
                        "required_item": "key1"
                    }
                }
            }
        ]
    }

    is_valid, errors = validate_scenario(valid_scenario)
    assert is_valid == True
    assert len(errors) == 0

def test_validate_scenario_missing_keys():
    invalid_scenario = {
        "title": "Test"
        # missing starting_room and rooms
    }
    is_valid, errors = validate_scenario(invalid_scenario)
    assert is_valid == False
    assert any("Missing required key: 'starting_room'" in e for e in errors)
    assert any("Missing required key: 'rooms'" in e for e in errors)

def test_validate_scenario_invalid_starting_room():
    invalid_scenario = {
        "title": "Test Game",
        "starting_room": "non_existent",
        "rooms": [{"id": "room1"}]
    }
    is_valid, errors = validate_scenario(invalid_scenario)
    assert is_valid == False
    assert any("Starting room 'non_existent' does not exist" in e for e in errors)

def test_validate_scenario_invalid_exit():
    invalid_scenario = {
        "title": "Test Game",
        "starting_room": "room1",
        "rooms": [
            {
                "id": "room1",
                "exits": {"north": "ghost_room"}
            }
        ]
    }
    is_valid, errors = validate_scenario(invalid_scenario)
    assert is_valid == False
    assert any("points to non-existent room 'ghost_room'" in e for e in errors)

def test_validate_scenario_missing_room_id():
    invalid_scenario = {
        "title": "Test Game",
        "starting_room": "room1",
        "rooms": [
            {"name": "No ID Room"}
        ]
    }
    is_valid, errors = validate_scenario(invalid_scenario)
    assert is_valid == False
    assert any("missing 'id'" in e for e in errors)
