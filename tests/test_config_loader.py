"""
Unit tests for the ConfigLoader class in core.config_loader.
"""
import pytest
import json
from unittest import mock # Using unittest.mock for patching
from selenium.webdriver.common.by import By
from core.config_loader import ConfigLoader, BY_MAPPING # Import BY_MAPPING for reference if needed
from core.logger import get_logger # To check logger names if necessary

# This ensures that the logger used in ConfigLoader is properly configured for capture by caplog
# if it wasn't already configured by some other part of the test setup.
# However, pytest's caplog should capture logs from loggers created by get_logger.
config_loader_logger = get_logger("core.config_loader") # Get the same logger instance

@pytest.fixture
def mock_config_loader_load(mocker):
    """
    Pytest fixture to mock the ConfigLoader.load static method.
    Allows controlling the raw data returned by ConfigLoader.load() for testing
    the transformation logic of load_selectors() independently.
    """
    # We are mocking 'core.config_loader.ConfigLoader.load'
    # This means when ConfigLoader.load_selectors calls ConfigLoader.load, it calls our mock.
    return mocker.patch('core.config_loader.ConfigLoader.load')

def test_load_selectors_valid_data(mock_config_loader_load):
    """
    Test ConfigLoader.load_selectors with well-formed input data.
    Verifies correct transformation of 'by' strings to By objects and
    preservation of 'value' strings.
    """
    mock_data = {
        "login_page": {
            "username_field": {"by": "name", "value": "username_input"},
            "password_field": {"by": "id", "value": "password_input"},
            "submit_button": {"by": "xpath", "value": "//button[@type='submit']"}
        },
        "home_page": {
            "welcome_message": {"by": "css_selector", "value": ".welcome-msg"},
            "profile_link": {"by": "link_text", "value": "View Profile"}
        },
        "common_elements": { # This page has no valid selectors, should not appear in output
            "app_version": "1.0.2",
            "login_url": "https://example.com/login" # Not a selector structure
        }
    }
    mock_config_loader_load.return_value = mock_data

    processed_selectors = ConfigLoader.load_selectors("dummy_selectors.json")

    assert "login_page" in processed_selectors
    assert "home_page" in processed_selectors

    # Check login_page selectors
    assert processed_selectors["login_page"]["username_field"] == (By.NAME, "username_input")
    assert processed_selectors["login_page"]["password_field"] == (By.ID, "password_input")
    assert processed_selectors["login_page"]["submit_button"] == (By.XPATH, "//button[@type='submit']")

    # Check home_page selectors
    assert processed_selectors["home_page"]["welcome_message"] == (By.CSS_SELECTOR, ".welcome-msg")
    assert processed_selectors["home_page"]["profile_link"] == (By.LINK_TEXT, "View Profile")

    # Check that common_elements page is not in processed_selectors because it had no valid structure
    # The current load_selectors only adds a page if it has valid processed_page_selectors.
    assert "common_elements" not in processed_selectors
    # Or, if it adds empty pages: assert not processed_selectors.get("common_elements")

    mock_config_loader_load.assert_called_once_with("dummy_selectors.json")

def test_load_selectors_invalid_by_string(mock_config_loader_load, caplog):
    """
    Test ConfigLoader.load_selectors with an invalid 'by' strategy string.
    Ensures the invalid selector is skipped and a warning is logged.
    """
    mock_data = {
        "login_page": {
            "username_field": {"by": "invalid_by_strategy", "value": "username_val"},
            "valid_field": {"by": "id", "value": "valid_id"}
        }
    }
    mock_config_loader_load.return_value = mock_data

    processed_selectors = ConfigLoader.load_selectors("dummy_invalid_by.json")

    assert "login_page" in processed_selectors # Page might still exist if other selectors are valid
    assert "username_field" not in processed_selectors["login_page"] # Invalid one skipped
    assert processed_selectors["login_page"]["valid_field"] == (By.ID, "valid_id") # Valid one processed

    assert "Invalid 'by' strategy 'invalid_by_strategy'" in caplog.text
    mock_config_loader_load.assert_called_once_with("dummy_invalid_by.json")

def test_load_selectors_missing_key(mock_config_loader_load, caplog):
    """
    Test ConfigLoader.load_selectors with selector data missing 'by' or 'value'.
    Ensures such selectors are skipped and warnings are logged.
    """
    mock_data = {
        "login_page": {
            "missing_value_field": {"by": "id"}, # 'value' is missing
            "missing_by_field": {"value": "some_value"}, # 'by' is missing
            "empty_value_field": {"by": "name", "value": ""}, # Empty 'value'
            "valid_field": {"by": "xpath", "value": "//div"}
        }
    }
    mock_config_loader_load.return_value = mock_data

    processed_selectors = ConfigLoader.load_selectors("dummy_missing_keys.json")

    assert "login_page" in processed_selectors
    assert "missing_value_field" not in processed_selectors["login_page"]
    assert "missing_by_field" not in processed_selectors["login_page"]
    # Empty value is currently treated as missing by "if not value_string"
    assert "empty_value_field" not in processed_selectors["login_page"]
    assert processed_selectors["login_page"]["valid_field"] == (By.XPATH, "//div")

    assert "Skipping selector 'missing_value_field'" in caplog.text
    assert "'value' (None) is missing or empty" in caplog.text # Specific part of message
    assert "Skipping selector 'missing_by_field'" in caplog.text
    assert "'by' (None) or 'value' (some_value) is missing or empty" in caplog.text # Specific part of message for by
    assert "Skipping selector 'empty_value_field'" in caplog.text
    assert "'value' () is missing or empty" in caplog.text # Specific part of message for empty value

    mock_config_loader_load.assert_called_once_with("dummy_missing_keys.json")

def test_load_selectors_empty_or_failed_load(mock_config_loader_load, caplog):
    """
    Test ConfigLoader.load_selectors when ConfigLoader.load returns empty or None.
    Ensures it returns an empty dictionary and logs a warning.
    """
    # Test case 1: ConfigLoader.load returns empty dictionary
    mock_config_loader_load.return_value = {}
    processed_selectors_empty = ConfigLoader.load_selectors("dummy_empty.json")
    assert processed_selectors_empty == {}
    assert "No data loaded from selector file: dummy_empty.json" in caplog.text
    caplog.clear() # Clear logs for the next case

    # Test case 2: ConfigLoader.load returns None (though current load returns {} on failure)
    # If ConfigLoader.load could return None, this would test it.
    # Given current ConfigLoader.load, this scenario is identical to empty dict.
    mock_config_loader_load.return_value = None
    processed_selectors_none = ConfigLoader.load_selectors("dummy_none.json")
    assert processed_selectors_none == {}
    assert "No data loaded from selector file: dummy_none.json" in caplog.text

    # Check that ConfigLoader.load was called for both scenarios
    assert mock_config_loader_load.call_count == 2


def test_load_selectors_malformed_page_data(mock_config_loader_load, caplog):
    """
    Test ConfigLoader.load_selectors with malformed page data (not a dictionary).
    """
    mock_data = {
        "login_page": "this_should_be_a_dict_of_selectors", # Malformed
        "home_page": {
            "title": {"by": "id", "value": "home_title"}
        }
    }
    mock_config_loader_load.return_value = mock_data
    processed_selectors = ConfigLoader.load_selectors("dummy_malformed.json")

    assert "login_page" not in processed_selectors
    assert "home_page" in processed_selectors
    assert processed_selectors["home_page"]["title"] == (By.ID, "home_title")
    assert "Skipping page 'login_page'" in caplog.text
    assert "expected a dictionary of selectors, got <class 'str'>" in caplog.text


def test_load_selectors_malformed_selector_data(mock_config_loader_load, caplog):
    """
    Test ConfigLoader.load_selectors with malformed selector data (not a dictionary).
    """
    mock_data = {
        "login_page": {
            "username": "this_should_be_a_dict_with_by_value", # Malformed
            "password": {"by": "id", "value": "pw"}
        }
    }
    mock_config_loader_load.return_value = mock_data
    processed_selectors = ConfigLoader.load_selectors("dummy_malformed_selector.json")

    assert "login_page" in processed_selectors
    assert "username" not in processed_selectors["login_page"]
    assert processed_selectors["login_page"]["password"] == (By.ID, "pw")
    assert "Skipping selector 'username' on page 'login_page'" in caplog.text
    assert "expected a dictionary, got <class 'str'>" in caplog.text

# Further tests could include:
# - Case insensitivity of "by" strings (e.g., "XPaTh" should work).
#   (The current implementation uses by_string.lower(), so this is covered)
# - Different valid "by" strategies from BY_MAPPING.
#   (test_load_selectors_valid_data covers a few, more could be added for completeness)
# - Nested structures if load_selectors were to support deeper hierarchies (currently it doesn't).
# - Test with an actual file read if not mocking ConfigLoader.load (integration test).
#   This would require creating temporary JSON files.
#   For that, pytest's tmp_path fixture would be useful.
#   Example:
#   def test_load_selectors_from_actual_file(tmp_path):
#       selector_content = { "page": { "element": {"by": "id", "value": "myid"}}}
#       d = tmp_path / "sub"
#       d.mkdir()
#       p = d / "selectors.json"
#       p.write_text(json.dumps(selector_content))
#       selectors = ConfigLoader.load_selectors(str(p))
#       assert selectors["page"]["element"] == (By.ID, "myid")

# Test for the BY_MAPPING specifically for 'css' alias
def test_by_mapping_css_alias():
    assert BY_MAPPING.get("css") == By.CSS_SELECTOR
    assert BY_MAPPING.get("css_selector") == By.CSS_SELECTOR

# Test that the logger instance is the same for consistency if needed elsewhere
# This is more of a meta-test about the logger setup.
def test_logger_instance_identity():
    from core.config_loader import config_loader_logger as cl_logger # Import the actual logger from module
    # This test assumes the logger name used in the module is exactly "core.config_loader"
    # If get_logger(__name__) is used, __name__ will be "core.config_loader" when run from project root.
    assert cl_logger.name == "core.config_loader"

# Test load method directly for file not found and JSON decode error
def test_config_loader_load_file_not_found(caplog, mocker):
    mocker.patch('os.path.exists', return_value=False)
    result = ConfigLoader.load("non_existent_file.json")
    assert result == {}
    assert "Configuration file not found: non_existent_file.json" in caplog.text

def test_config_loader_load_json_decode_error(tmp_path, caplog):
    p = tmp_path / "malformed.json"
    p.write_text("{'invalid_json': 'this is not valid json'}") # Single quotes are invalid

    result = ConfigLoader.load(str(p))
    assert result == {}
    assert f"Error decoding JSON from {p}" in caplog.text

def test_config_loader_load_unsupported_file_type(tmp_path, caplog):
    p = tmp_path / "settings.txt"
    p.write_text("data=value")
    result = ConfigLoader.load(str(p))
    assert result == {}
    assert f"File type not supported for loading: {p}" in caplog.text

# (The ConfigLoader.load method was enhanced in a previous step, so adding tests for it here)
