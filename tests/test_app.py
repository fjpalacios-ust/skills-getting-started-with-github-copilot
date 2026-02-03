"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    
    # Store original state
    original_activities = {
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
        "Basketball": {
            "description": "Team sport focusing on basketball skills and competitive play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis techniques and participate in matches",
            "schedule": "Saturdays, 10:00 AM - 11:30 AM",
            "max_participants": 10,
            "participants": ["james@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Wednesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Create visual art including painting, drawing, and sculpture",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["sophie@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:45 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore scientific concepts through experiments and projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ethan@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Restore after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9
    
    def test_activities_have_required_fields(self, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
    
    def test_activities_have_participants(self, reset_activities):
        """Test that activities contain participants"""
        response = client.get("/activities")
        data = response.json()
        
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, reset_activities):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant(self, reset_activities):
        """Test that signup actually adds the participant"""
        client.post(
            "/activities/Basketball/signup?email=newplayer@mergington.edu",
            headers={"Content-Type": "application/json"}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "newplayer@mergington.edu" in data["Basketball"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, reset_activities):
        """Test signing up for a nonexistent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_email(self, reset_activities):
        """Test signing up with an email already registered"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_multiple_signups(self, reset_activities):
        """Test multiple students signing up"""
        client.post(
            "/activities/Tennis%20Club/signup?email=student1@mergington.edu",
            headers={"Content-Type": "application/json"}
        )
        client.post(
            "/activities/Tennis%20Club/signup?email=student2@mergington.edu",
            headers={"Content-Type": "application/json"}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert len(data["Tennis Club"]["participants"]) == 3
        assert "student1@mergington.edu" in data["Tennis Club"]["participants"]
        assert "student2@mergington.edu" in data["Tennis Club"]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_successful_removal(self, reset_activities):
        """Test successfully removing a participant"""
        response = client.delete(
            "/activities/Chess%20Club/participants/michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        assert "michael@mergington.edu" in data["message"]
    
    def test_removal_updates_participants_list(self, reset_activities):
        """Test that removal actually removes the participant"""
        client.delete(
            "/activities/Drama%20Club/participants/isabella@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "isabella@mergington.edu" not in data["Drama Club"]["participants"]
        assert len(data["Drama Club"]["participants"]) == 1
    
    def test_remove_from_nonexistent_activity(self, reset_activities):
        """Test removing from a nonexistent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Club/participants/student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_remove_nonexistent_participant(self, reset_activities):
        """Test removing a participant who's not signed up"""
        response = client.delete(
            "/activities/Chess%20Club/participants/notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_remove_multiple_participants(self, reset_activities):
        """Test removing multiple participants"""
        client.delete(
            "/activities/Debate%20Team/participants/noah@mergington.edu"
        )
        client.delete(
            "/activities/Debate%20Team/participants/ava@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        assert len(data["Debate Team"]["participants"]) == 0
