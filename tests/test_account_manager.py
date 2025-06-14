"""
Unit tests for the CoreAccountManager class in core.account_manager.
"""
import pytest
from unittest import mock # Using unittest.mock for patching
from core.account_manager import CoreAccountManager
# Logger from the module being tested to check its output
from core.account_manager import account_manager_logger as manager_logger

@pytest.fixture
def mock_config_loader_load(mocker):
    """
    Pytest fixture to mock core.config_loader.ConfigLoader.load.
    This prevents actual file I/O during tests and allows controlled return values.
    """
    return mocker.patch('core.config_loader.ConfigLoader.load')

# --- Tests for __init__ and _load_accounts_from_file ---

def test_init_successful_load(mock_config_loader_load, caplog):
    """Test __init__ with successful loading of accounts from JSON."""
    mock_data = {
        "user1": {"pass": "pass123", "email": "user1@example.com"},
        "user2": {"password": "securepassword", "role": "admin"} # Using 'password' as alternative key
    }
    mock_config_loader_load.return_value = mock_data

    manager = CoreAccountManager(filepath="dummy_accounts.json")

    assert len(manager.accounts) == 2
    assert manager.current_account_index == 0

    # Check user1
    acc1 = next(acc for acc in manager.accounts if acc["username"] == "user1")
    assert acc1["password"] == "pass123"
    assert acc1["status"] == "new"
    assert acc1["status_details"] == {}
    assert acc1["full_details"]["email"] == "user1@example.com"

    # Check user2
    acc2 = next(acc for acc in manager.accounts if acc["username"] == "user2")
    assert acc2["password"] == "securepassword"
    assert acc2["status"] == "new"
    assert acc2["full_details"]["role"] == "admin"

    mock_config_loader_load.assert_called_once_with("dummy_accounts.json")
    assert f"Successfully loaded 2 accounts from 'dummy_accounts.json'." in caplog.text
    assert f"Processed 2 accounts from 'dummy_accounts.json'." in caplog.text


def test_init_load_malformed_account_missing_pass(mock_config_loader_load, caplog):
    """Test __init__ when an account in JSON is missing 'pass' or 'password' key."""
    mock_data = {
        "user_ok": {"pass": "goodpass"},
        "user_bad": {"email": "user_bad@example.com"} # Missing 'pass'/'password'
    }
    mock_config_loader_load.return_value = mock_data

    manager = CoreAccountManager("malformed.json")

    assert len(manager.accounts) == 1
    assert manager.accounts[0]["username"] == "user_ok"
    assert f"Skipping account 'user_bad': 'pass' or 'password' key not found" in caplog.text
    assert f"Processed 1 accounts from 'malformed.json'." in caplog.text


def test_init_load_account_details_not_dict(mock_config_loader_load, caplog):
    """Test __init__ when an account's details in JSON are not a dictionary."""
    mock_data = {
        "user_ok": {"pass": "goodpass"},
        "user_bad": "this_should_be_a_dict"
    }
    mock_config_loader_load.return_value = mock_data

    manager = CoreAccountManager("not_dict.json")

    assert len(manager.accounts) == 1
    assert manager.accounts[0]["username"] == "user_ok"
    assert "Skipping account 'user_bad': details are not a dictionary." in caplog.text

def test_init_load_raw_data_not_dict(mock_config_loader_load, caplog):
    """Test __init__ when the raw data loaded from JSON is not a dictionary itself."""
    mock_data = ["list", "of", "strings"] # Should be a dict of accounts
    mock_config_loader_load.return_value = mock_data

    manager = CoreAccountManager("list_data.json")

    assert len(manager.accounts) == 0
    assert "Account data in 'list_data.json' is not a dictionary" in caplog.text
    assert "No accounts loaded from 'list_data.json'." in caplog.text # From __init__ summary log

def test_init_load_empty_or_failed(mock_config_loader_load, caplog):
    """Test __init__ when ConfigLoader.load returns an empty dict (e.g., file empty or error)."""
    mock_config_loader_load.return_value = {} # Simulate empty or failed load

    manager = CoreAccountManager("empty.json")

    assert len(manager.accounts) == 0
    assert "No data or invalid data found in accounts file: empty.json" in caplog.text
    assert "No accounts loaded from 'empty.json'." in caplog.text


# --- Tests for add_account ---

def test_add_account_manually(mock_config_loader_load):
    """Test adding an account manually using add_account method."""
    mock_config_loader_load.return_value = {} # Ensure __init__ starts with empty list
    manager = CoreAccountManager() # Use default filepath, but it will be empty due to mock

    manager.add_account("new_user", "new_pass", role="tester", source="manual")

    assert len(manager.accounts) == 1
    added_acc = manager.accounts[0]
    assert added_acc["username"] == "new_user"
    assert added_acc["password"] == "new_pass"
    assert added_acc["status"] == "new"
    assert added_acc["status_details"] == {}
    assert added_acc["full_details"]["role"] == "tester"
    assert added_acc["full_details"]["source"] == "manual"
    assert added_acc["full_details"]["pass"] == "new_pass" # 'pass' key is prioritized

def test_add_account_invalid_input(mock_config_loader_load):
    """Test add_account with invalid (non-string) username or password."""
    mock_config_loader_load.return_value = {}
    manager = CoreAccountManager()

    with pytest.raises(ValueError, match="Username and password must be strings."):
        manager.add_account(123, "password") # Invalid username
    with pytest.raises(ValueError, match="Username and password must be strings."):
        manager.add_account("user", None) # Invalid password


# --- Tests for get_next_account and reset_account_cycle ---

def test_get_next_account_cycling_and_reset(mock_config_loader_load, caplog):
    """Test account cycling with get_next_account and resetting with reset_account_cycle."""
    mock_data = {
        "acc1": {"pass": "p1"},
        "acc2": {"pass": "p2"}
    }
    mock_config_loader_load.return_value = mock_data
    manager = CoreAccountManager()

    assert manager.current_account_index == 0

    acc_one = manager.get_next_account()
    assert acc_one is not None
    assert acc_one["username"] == "acc1" # Order might vary based on dict iteration, adjust if needed or sort keys in _load
    assert manager.current_account_index == 1
    assert f"Returning account '{acc_one['username']}' (index 0). Next index: 1." in caplog.text
    caplog.clear()

    acc_two = manager.get_next_account()
    assert acc_two is not None
    # To make this test deterministic if dict iteration order is an issue:
    # We can check that the returned set of usernames is as expected.
    # For now, assuming order based on simple mock_data.
    if acc_one["username"] == "acc1":
         assert acc_two["username"] == "acc2"
    else:
         assert acc_two["username"] == "acc1"
    assert manager.current_account_index == 2
    assert f"Returning account '{acc_two['username']}' (index 1). Next index: 2." in caplog.text
    caplog.clear()

    acc_none = manager.get_next_account()
    assert acc_none is None
    assert manager.current_account_index == 2 # Index remains at the end
    assert "All accounts have been cycled through." in caplog.text
    caplog.clear()

    manager.reset_account_cycle()
    assert manager.current_account_index == 0
    assert "Resetting account cycle." in caplog.text
    caplog.clear()

    acc_one_again = manager.get_next_account()
    assert acc_one_again is not None
    # This should be the first account again, matching acc_one or the other if order varied.
    # A more robust check might involve sorting self.accounts by username in __init__ if needed for tests.
    first_loaded_username = sorted(mock_data.keys())[0]
    assert acc_one_again["username"] == first_loaded_username
    assert manager.current_account_index == 1

def test_get_next_account_empty_list(mock_config_loader_load, caplog):
    """Test get_next_account when the accounts list is empty."""
    mock_config_loader_load.return_value = {}
    manager = CoreAccountManager()

    assert manager.get_next_account() is None
    assert "get_next_account called but no accounts are loaded." in caplog.text


# --- Tests for update_account_status ---

def test_update_account_status_existing_account(mock_config_loader_load, caplog):
    """Test updating status and status_details for an existing account."""
    mock_config_loader_load.return_value = {"user_x": {"pass": "px"}}
    manager = CoreAccountManager()

    # Update with dict status_info
    update_info_dict = {"last_error": "Login failed", "attempts": 3}
    result = manager.update_account_status("user_x", "error_login", status_info=update_info_dict)
    assert result is True

    acc_x = manager.accounts[0]
    assert acc_x["status"] == "error_login"
    assert acc_x["status_details"]["last_error"] == "Login failed"
    assert acc_x["status_details"]["attempts"] == 3
    assert f"Status for account 'user_x' updated to 'error_login'. Details: {update_info_dict}" in caplog.text
    caplog.clear()

    # Update with string status_info (should be stored under 'message')
    update_info_str = "Account temporarily locked."
    result_str = manager.update_account_status("user_x", "cooldown", status_info=update_info_str)
    assert result_str is True
    assert acc_x["status"] == "cooldown"
    assert acc_x["status_details"]["message"] == update_info_str
    assert f"Status for account 'user_x' updated to 'cooldown'. Message: {update_info_str}" in caplog.text
    caplog.clear()

    # Update status_details again, merging
    update_info_dict_2 = {"cooldown_until": "10:00"}
    manager.update_account_status("user_x", "cooldown_active", status_info=update_info_dict_2)
    assert acc_x["status_details"]["message"] == update_info_str # Previous message should persist
    assert acc_x["status_details"]["cooldown_until"] == "10:00" # New detail added

def test_update_account_status_non_existing_account(mock_config_loader_load, caplog):
    """Test updating status for a non-existing account."""
    mock_config_loader_load.return_value = {"user_y": {"pass": "py"}}
    manager = CoreAccountManager()

    result = manager.update_account_status("non_user_z", "active")
    assert result is False
    assert "Attempted to update status for account 'non_user_z', but account was not found." in caplog.text
    assert manager.accounts[0]["status"] == "new" # Original account status unchanged
