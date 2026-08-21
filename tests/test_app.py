from src.app import activities

SEED_ACTIVITY = "Chess Club"
SEED_PARTICIPANT = "michael@mergington.edu"


def test_root_redirects_to_static_index(client):
    # Arrange
    # (no setup needed)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (302, 303, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_seed_data(client):
    # Arrange
    # (activities dict already seeded via app import)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert SEED_ACTIVITY in body
    activity = body[SEED_ACTIVITY]
    assert {"description", "schedule", "max_participants", "participants"} <= activity.keys()


def test_signup_for_activity_success(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{SEED_ACTIVITY}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {SEED_ACTIVITY}"}
    assert email in activities[SEED_ACTIVITY]["participants"]


def test_signup_for_activity_duplicate_fails(client):
    # Arrange
    email = SEED_PARTICIPANT  # already signed up in seed data

    # Act
    response = client.post(f"/activities/{SEED_ACTIVITY}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_unknown_activity_fails(client):
    # Arrange
    email = "someone@mergington.edu"

    # Act
    response = client.post("/activities/Not A Real Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_full_activity_fails(client):
    # Arrange
    activities[SEED_ACTIVITY]["max_participants"] = len(activities[SEED_ACTIVITY]["participants"])

    # Act
    response = client.post(f"/activities/{SEED_ACTIVITY}/signup", params={"email": "late@mergington.edu"})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_from_activity_success(client):
    # Arrange
    email = SEED_PARTICIPANT  # already signed up in seed data

    # Act
    response = client.delete(f"/activities/{SEED_ACTIVITY}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {SEED_ACTIVITY}"}
    assert email not in activities[SEED_ACTIVITY]["participants"]


def test_unregister_not_registered_fails(client):
    # Arrange
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(f"/activities/{SEED_ACTIVITY}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_from_unknown_activity_fails(client):
    # Arrange
    email = "someone@mergington.edu"

    # Act
    response = client.delete("/activities/Not A Real Club/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
