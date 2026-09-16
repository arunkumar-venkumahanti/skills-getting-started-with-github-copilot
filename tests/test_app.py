from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_details(client):
    # Arrange
    activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activity_data = response.json()[activity]
    assert activity_data["description"]
    assert activity_data["schedule"]
    assert activity_data["max_participants"] == 12
    assert "michael@mergington.edu" in activity_data["participants"]


def test_signup_adds_participant(client):
    # Arrange
    activity = "Soccer Club"
    email = "student@example.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in client.get("/activities").json()[activity]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up for this activity"}


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity = "Unknown Club"
    email = "student@example.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "student@example.edu"
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity}"}
    assert email not in client.get("/activities").json()[activity]["participants"]


def test_unregister_rejects_nonparticipant(client):
    # Arrange
    activity = "Chess Club"
    email = "student@example.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity = "Unknown Club"
    email = "student@example.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
