"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from src.app import activities
    
    initial_state = {
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
        "Basketball Team": {
            "description": "Competitive basketball team for varsity and JV players",
            "schedule": "Mondays, Wednesdays, Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and compete in friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["sarah@mergington.edu", "james@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Play instruments and perform in concerts",
            "schedule": "Tuesdays and Thursdays, 4:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "grace@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills through competitive debate",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["noah@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore advanced topics in science",
            "schedule": "Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(initial_state)
    
    yield


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_all_activities(self, client, reset_activities):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that we have activities
        assert len(data) > 0
        
        # Check that Chess Club exists
        assert "Chess Club" in data
        assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
        assert data["Chess Club"]["max_participants"] == 12
        assert len(data["Chess Club"]["participants"]) > 0
    
    def test_activities_contain_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client, reset_activities):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_updates_participants_list(self, client, reset_activities):
        """Test that signup actually adds the student to participants list"""
        from src.app import activities
        
        email = "newstudent@mergington.edu"
        response = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify the student was added
        assert email in activities["Programming Class"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client, reset_activities):
        """Test signup for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_duplicate_signup(self, client, reset_activities):
        """Test that duplicate signup is rejected"""
        # michael@mergington.edu is already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test signing up multiple different students"""
        from src.app import activities
        
        initial_count = len(activities["Gym Class"]["participants"])
        
        # Sign up first student
        response1 = client.post(
            "/activities/Gym Class/signup?email=student1@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Sign up second student
        response2 = client.post(
            "/activities/Gym Class/signup?email=student2@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both were added
        assert "student1@mergington.edu" in activities["Gym Class"]["participants"]
        assert "student2@mergington.edu" in activities["Gym Class"]["participants"]
        assert len(activities["Gym Class"]["participants"]) == initial_count + 2


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_successful_unregister(self, client, reset_activities):
        """Test successfully unregistering from an activity"""
        response = client.delete(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_from_participants(self, client, reset_activities):
        """Test that unregister actually removes the student"""
        from src.app import activities
        
        email = "michael@mergington.edu"
        response = client.delete(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify the student was removed
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client, reset_activities):
        """Test unregister from a non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_student_not_signed_up(self, client, reset_activities):
        """Test unregistering a student who is not signed up"""
        response = client.delete(
            "/activities/Chess Club/signup?email=notstudent@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_preserves_other_participants(self, client, reset_activities):
        """Test that unregistering one student doesn't affect others"""
        from src.app import activities
        
        initial_participants = activities["Chess Club"]["participants"].copy()
        
        # Unregister one student
        client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
        
        # Check that other participants remain
        remaining = activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in remaining
        assert len(remaining) == len(initial_participants) - 1


class TestSignupUnregisterFlow:
    """Integration tests for signup and unregister flows"""
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up and then unregistering"""
        from src.app import activities
        
        email = "testflow@mergington.edu"
        activity = "Basketball Team"
        
        # Sign up
        response1 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response1.status_code == 200
        assert email in activities[activity]["participants"]
        
        # Unregister
        response2 = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response2.status_code == 200
        assert email not in activities[activity]["participants"]
    
    def test_signup_unregister_then_signup_again(self, client, reset_activities):
        """Test that a student can sign up again after unregistering"""
        from src.app import activities
        
        email = "testflow2@mergington.edu"
        activity = "Tennis Club"
        
        # Sign up
        response1 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response3.status_code == 200
        assert email in activities[activity]["participants"]
