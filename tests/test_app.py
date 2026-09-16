from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_unsubscribe_participant_from_activity():
    activity = "Chess Club"
    email = "student@example.edu"

    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200

    response = client.delete(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]
