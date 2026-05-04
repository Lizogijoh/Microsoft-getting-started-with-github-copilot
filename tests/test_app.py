import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state after each test to ensure isolation."""
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Swim training and lap practice for all levels",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["nina@mergington.edu", "ethan@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and mixed media art projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu", "mia@mergington.edu"]
        },
        "Drama Society": {
            "description": "Rehearse scenes, build stagecraft skills, and perform",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["jack@mergington.edu", "lily@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Prepare for math competitions with challenging problem solving",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["sophia@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["lucas@mergington.edu", "maya@mergington.edu"]
        },
        "Science Fair": {
            "description": "Conduct experiments and prepare projects for science fairs",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["liam@mergington.edu", "isabella@mergington.edu"]
        }
    }
    # Replace the global activities dict
    activities.clear()
    activities.update(initial_activities)
    yield
    # No need to reset as autouse will do it before each test


def test_get_activities():
    """Test retrieving all activities."""
    # Arrange - no special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # All activities present
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_success():
    """Test successful signup for an activity."""
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    """Test signup when student is already registered."""
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]
    # Ensure not added twice
    assert activities[activity]["participants"].count(email) == 1


def test_signup_invalid_activity():
    """Test signup for non-existent activity."""
    # Arrange
    activity = "NonExistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_unregister_success():
    """Test successful unregistration from an activity."""
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]
    assert email not in activities[activity]["participants"]


def test_unregister_not_enrolled():
    """Test unregistration when student is not enrolled."""
    # Arrange
    activity = "Chess Club"
    email = "notenrolled@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "not signed up" in result["detail"]


def test_unregister_invalid_activity():
    """Test unregistration from non-existent activity."""
    # Arrange
    activity = "NonExistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_signup_after_unregister():
    """Test signup works after unregistration."""
    # Arrange
    activity = "Programming Class"
    email = "emma@mergington.edu"  # Initially enrolled

    # Act - Unregister first
    client.delete(f"/activities/{activity}/participants/{email}")
    # Then signup again
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]