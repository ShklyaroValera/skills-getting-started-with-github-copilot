from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_get_activities_contains_known_activity():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_adds_participant():
    activity = "Tennis Club"
    email = "test.user@example.com"
    # ensure clean state
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert email in activities[activity]["participants"]
    assert f"Signed up {email}" in r.json().get("message", "")


def test_duplicate_signup_returns_400():
    activity = "Chess Club"
    existing = activities[activity]["participants"][0]
    before = list(activities[activity]["participants"])

    r = client.post(f"/activities/{activity}/signup", params={"email": existing})
    assert r.status_code == 400
    assert "already signed up" in r.json().get("detail", "")
    assert activities[activity]["participants"] == before


def test_remove_participant_success():
    activity = "Basketball Team"
    email = activities[activity]["participants"][0]
    # ensure present
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    r = client.delete(f"/activities/{activity}/participant", params={"email": email})
    assert r.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_nonexistent_participant_returns_400():
    activity = "Art Studio"
    email = "not.signed@example.com"
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    r = client.delete(f"/activities/{activity}/participant", params={"email": email})
    assert r.status_code == 400
    assert "not signed up" in r.json().get("detail", "")


def test_404_on_nonexistent_activity():
    activity = "Nonexistent Club"
    r1 = client.post(f"/activities/{activity}/signup", params={"email": "x@y.com"})
    assert r1.status_code == 404
    r2 = client.delete(f"/activities/{activity}/participant", params={"email": "x@y.com"})
    assert r2.status_code == 404


def test_root_redirects_to_static_index():
    # Do not follow redirects so we can assert the redirect response
    r = client.get("/", follow_redirects=False)
    assert r.status_code in (307, 302)
    assert r.headers.get("location", "").endswith("/static/index.html")
