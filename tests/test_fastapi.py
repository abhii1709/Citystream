# test_traffic_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import mock_open, patch
import json
from datetime import datetime
from app.main import app, TrafficRecord
client = TestClient(app)

# Sample test data
SAMPLE_DATA = [
    {
        "timestamp": "2023-01-01T08:00:00",
        "location": "Main Street",
        "vehicle_count": "150",
        "avg_speed_kmph": "45.5",
        "congestion_level": "moderate",
        "weather": "sunny",
        "accidents_reported": "1"
    },
    {
        "timestamp": "2023-01-01T09:00:00",
        "location": "Second Avenue",
        "vehicle_count": "200",
        "avg_speed_kmph": "30.0",
        "congestion_level": "high",
        "weather": "rainy",
        "accidents_reported": "2"
    }
]


@pytest.fixture
def mock_file():
    # Mock the file operations with our sample data
    with patch("builtins.open", mock_open(read_data=json.dumps(SAMPLE_DATA))) as mock_file:
        yield mock_file


def test_get_all_records(mock_file):
    response = client.get("/records")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["location"] == "Main Street"


def test_get_records_with_filters(mock_file):
    # Test location filter
    response = client.get("/records?location=Main Street")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["location"] == "Main Street"

    # Test congestion level filter
    response = client.get("/records?congestion_level=moderate")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["congestion_level"] == "moderate"


def test_get_single_record(mock_file):
    response = client.get("/records/Main Street")
    assert response.status_code == 200
    assert response.json()["location"] == "Main Street"

    # Test non-existent record
    response = client.get("/records/Nonexistent Street")
    assert response.status_code == 404


def test_create_record(mock_file):
    new_record = {
        "timestamp": "2023-01-01T10:00:00",
        "location": "Third Avenue",
        "vehicle_count": "250",
        "avg_speed_kmph": "35.0",
        "congestion_level": "low",
        "weather": "cloudy",
        "accidents_reported": "0"
    }

    response = client.post("/records", json=new_record)
    assert response.status_code == 200
    assert response.json()["location"] == "Third Avenue"

    # Test duplicate record creation
    response = client.post("/records", json=SAMPLE_DATA[0])
    assert response.status_code == 400


def test_update_record(mock_file):
    updated_data = {
        "timestamp": SAMPLE_DATA[0]["timestamp"],
        "location": SAMPLE_DATA[0]["location"],
        "vehicle_count": "300",
        "avg_speed_kmph": "50.0",
        "congestion_level": "high",
        "weather": "cloudy",
        "accidents_reported": "2"
    }

    response = client.put(
        f"/records/{SAMPLE_DATA[0]['location']}/{SAMPLE_DATA[0]['timestamp']}",
        json=updated_data
    )
    assert response.status_code == 200
    assert response.json()["vehicle_count"] == "300"

    # Test invalid update (changing location)
    invalid_update = updated_data.copy()
    invalid_update["location"] = "New Location"
    response = client.put(
        f"/records/{SAMPLE_DATA[0]['location']}/{SAMPLE_DATA[0]['timestamp']}",
        json=invalid_update
    )
    assert response.status_code == 400


def test_delete_record(mock_file):
    response = client.delete(
        f"/records/{SAMPLE_DATA[0]['location']}/{SAMPLE_DATA[0]['timestamp']}"
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Record deleted"

    # Test deleting non-existent record
    response = client.delete("/records/Nonexistent/2023-01-01T00:00:00")
    assert response.status_code == 404


def test_invalid_data_handling(mock_file):
    # Test missing required field
    invalid_record = {
        "timestamp": "2023-01-01T11:00:00",
        # Missing location
        "vehicle_count": "100",
        "avg_speed_kmph": "40.0",
        "congestion_level": "moderate",
        "weather": "sunny",
        "accidents_reported": "0"
    }
    response = client.post("/records", json=invalid_record)
    assert response.status_code == 422

