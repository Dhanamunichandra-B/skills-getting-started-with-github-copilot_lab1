"""
Pytest tests for the FastAPI High School Management System API.
Uses AAA pattern: Arrange, Act, Assert
Tests endpoints: GET /activities, POST signup, DELETE remove participant
"""
import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Test suite for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Test that GET /activities returns all activities.
        
        Arrange: No setup needed, activities are pre-populated
        Act: Send GET request to /activities
        Assert: Response status is 200 and contains all activities
        """
        # Arrange
        expected_activity_count = 9
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == expected_activity_count
        assert "Chess Club" in response.json()
        assert "Basketball Team" in response.json()
        assert "Science Club" in response.json()
    
    def test_get_activities_contains_correct_fields(self, client, reset_activities):
        """
        Test that activity objects contain all required fields.
        
        Arrange: No setup needed
        Act: Send GET request and retrieve an activity
        Assert: Activity has description, schedule, max_participants, and participants
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        first_activity = activities["Chess Club"]
        
        # Assert
        assert set(first_activity.keys()) == required_fields
        assert isinstance(first_activity["participants"], list)
        assert len(first_activity["participants"]) == 2


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client, reset_activities):
        """
        Test successful signup for an activity.
        
        Arrange: Prepare a student email and activity with available slots
        Act: Send POST request to signup endpoint
        Assert: Response status is 200 and participant is added
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "alex@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in reset_activities[activity_name]["participants"]
    
    def test_signup_duplicate_error(self, client, reset_activities):
        """
        Test signup fails when student is already registered.
        
        Arrange: Student is already in participants list
        Act: Send POST request with same email
        Assert: Response status is 400 with appropriate error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"
    
    def test_signup_activity_not_found_error(self, client, reset_activities):
        """
        Test signup fails when activity doesn't exist.
        
        Arrange: Use non-existent activity name
        Act: Send POST request for non-existent activity
        Assert: Response status is 404 with not found error
        """
        # Arrange
        activity_name = "Non-existent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRemoveParticipant:
    """Test suite for DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_remove_participant_success(self, client, reset_activities):
        """
        Test successful removal of participant from activity.
        
        Arrange: Participant is in the activity participants list
        Act: Send DELETE request to remove participant
        Assert: Response status is 200 and participant is removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(reset_activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in reset_activities[activity_name]["participants"]
        assert len(reset_activities[activity_name]["participants"]) == initial_count - 1
    
    def test_remove_participant_not_found_in_activity(self, client, reset_activities):
        """
        Test removal fails when participant is not in the activity.
        
        Arrange: Email is not in activity participants list
        Act: Send DELETE request for non-participant
        Assert: Response status is 404 with participant not found error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
    
    def test_remove_participant_activity_not_found_error(self, client, reset_activities):
        """
        Test removal fails when activity doesn't exist.
        
        Arrange: Use non-existent activity name
        Act: Send DELETE request for non-existent activity
        Assert: Response status is 404 with activity not found error
        """
        # Arrange
        activity_name = "Non-existent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
