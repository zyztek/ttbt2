"""
Unit tests for the EngagementManager class in interactions.engagement.
"""
import pytest
from interactions.engagement import EngagementManager
# Logger from the module being tested to check its output
from interactions.engagement import engagement_logger as manager_logger # Assuming this is how it's named

# --- Test for __init__ ---

def test_engagement_manager_init(caplog):
    """Test the initialization of EngagementManager."""
    manager = EngagementManager()
    assert isinstance(manager.engaged_users, set), "engaged_users should be a set."
    assert len(manager.engaged_users) == 0, "engaged_users should be empty initially."
    assert "EngagementManager initialized." in caplog.text

# --- Tests for engage_user ---

def test_engage_user_new_and_existing(caplog):
    """Test engaging a new user and then the same user again."""
    manager = EngagementManager()
    caplog.clear() # Clear init log

    # Engage a new user
    manager.engage_user("user123")
    assert "user123" in manager.engaged_users
    assert len(manager.engaged_users) == 1
    assert f"User 'user123' marked as engaged. Total engaged users: 1." in caplog.text
    caplog.clear()

    # Engage the same user again
    manager.engage_user("user123")
    assert "user123" in manager.engaged_users # Still present
    assert len(manager.engaged_users) == 1 # Count should not change
    assert f"User 'user123' was already marked as engaged." in caplog.text # Check for trace log
    caplog.clear()

    # Engage another new user
    manager.engage_user("user456")
    assert "user456" in manager.engaged_users
    assert len(manager.engaged_users) == 2
    assert f"User 'user456' marked as engaged. Total engaged users: 2." in caplog.text

def test_engage_user_with_none(caplog):
    """Test calling engage_user with None as user_id."""
    manager = EngagementManager()
    caplog.clear() # Clear init log

    manager.engage_user(None)
    assert None not in manager.engaged_users # Should not add None
    assert len(manager.engaged_users) == 0
    assert "Attempted to engage with a None user_id." in caplog.text

# --- Tests for has_engaged ---

def test_has_engaged_scenarios(caplog):
    """Test has_engaged for various scenarios."""
    manager = EngagementManager()
    manager.engage_user("engaged_user_A")
    caplog.clear() # Clear init and engage logs

    # Test with an engaged user
    assert manager.has_engaged("engaged_user_A") is True
    assert f"Checking engagement for user 'engaged_user_A': True" in caplog.text
    caplog.clear()

    # Test with a non-engaged user
    assert manager.has_engaged("non_engaged_user_B") is False
    assert f"Checking engagement for user 'non_engaged_user_B': False" in caplog.text
    caplog.clear()

    # Test with None user_id
    assert manager.has_engaged(None) is False
    assert "has_engaged called with None user_id, returning False." in caplog.text

# --- Tests for get_engaged_count ---

def test_get_engaged_count(caplog):
    """Test the accuracy of get_engaged_count."""
    manager = EngagementManager()

    # Test with empty set
    assert manager.get_engaged_count() == 0
    assert "Current engaged user count: 0" in caplog.text
    caplog.clear()

    manager.engage_user("user_alpha")
    manager.engage_user("user_beta")
    assert manager.get_engaged_count() == 2
    assert "Current engaged user count: 2" in caplog.text
    caplog.clear()

    manager.engage_user("user_alpha") # Engage existing user
    assert manager.get_engaged_count() == 2 # Count should remain the same
    assert "Current engaged user count: 2" in caplog.text


# --- Tests for clear_engagement_history ---

def test_clear_engagement_history(caplog):
    """Test clearing the engagement history."""
    manager = EngagementManager()
    manager.engage_user("temp_user1")
    manager.engage_user("temp_user2")
    assert manager.get_engaged_count() == 2
    caplog.clear() # Clear previous logs

    manager.clear_engagement_history()
    assert manager.get_engaged_count() == 0
    assert len(manager.engaged_users) == 0
    assert "Engagement history cleared. 2 users were removed from history." in caplog.text
    caplog.clear()

    # Check if has_engaged reflects the cleared history
    assert manager.has_engaged("temp_user1") is False
    assert "Checking engagement for user 'temp_user1': False" in caplog.text
    caplog.clear()

    # Clear an already empty history
    manager.clear_engagement_history()
    assert manager.get_engaged_count() == 0
    assert "Engagement history cleared. 0 users were removed from history." in caplog.text
