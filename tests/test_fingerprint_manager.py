"""
Unit tests for the FingerprintManager class in fingerprints.fingerprint_manager.
"""
import pytest
from unittest import mock
from fingerprints.fingerprint_manager import FingerprintManager
# Logger from the module being tested to check its output
from fingerprints.fingerprint_manager import fingerprint_manager_logger as manager_logger

@pytest.fixture
def mock_config_loader_load(mocker):
    """
    Pytest fixture to mock core.config_loader.ConfigLoader.load.
    This prevents actual file I/O during tests and allows controlled return values.
    """
    return mocker.patch('core.config_loader.ConfigLoader.load')

# --- Tests for __init__ ---

def test_init_direct_list():
    """Test __init__ with a directly provided list of fingerprints."""
    direct_fingerprints = ["Mozilla/5.0 (FP1)", "Mozilla/5.0 (FP2)"]
    manager = FingerprintManager(fingerprints=direct_fingerprints, filepath="dummy_fp_path.json") # filepath won't be used

    assert manager.fingerprints == direct_fingerprints
    # No call to ConfigLoader.load should have been made if fingerprints list is passed

def test_init_load_from_json_success(mock_config_loader_load, caplog):
    """Test __init__ with successful loading of fingerprints from JSON."""
    mock_data = {"fingerprints": ["UA_JSON_1", "UA_JSON_2", "UA_JSON_3"]}
    mock_config_loader_load.return_value = mock_data

    manager = FingerprintManager(filepath="valid_fingerprints.json") # fingerprints=None by default

    assert manager.fingerprints == mock_data["fingerprints"]
    mock_config_loader_load.assert_called_once_with("valid_fingerprints.json")
    assert f"Successfully loaded {len(mock_data['fingerprints'])} fingerprints" in caplog.text

def test_init_load_from_json_malformed_data(mock_config_loader_load, caplog):
    """Test __init__ when JSON data is malformed."""
    # Case 1: 'fingerprints' key missing
    mock_config_loader_load.return_value = {"other_key": ["data"]}
    manager_case1 = FingerprintManager(filepath="malformed_fp1.json")
    assert manager_case1.fingerprints == []
    assert "Failed to load fingerprints from 'malformed_fp1.json'" in caplog.text
    caplog.clear()

    # Case 2: 'fingerprints' is not a list
    mock_config_loader_load.return_value = {"fingerprints": "this_should_be_a_list_of_strings"}
    manager_case2 = FingerprintManager(filepath="malformed_fp2.json")
    assert manager_case2.fingerprints == []
    assert "Failed to load fingerprints from 'malformed_fp2.json'" in caplog.text
    caplog.clear()

    # Case 3: Loaded data is not a dictionary
    mock_config_loader_load.return_value = ["just_a_list_not_a_dict_of_fingerprints"]
    manager_case3 = FingerprintManager(filepath="malformed_fp3.json")
    assert manager_case3.fingerprints == []
    assert "Failed to load fingerprints from 'malformed_fp3.json'" in caplog.text

def test_init_load_from_json_empty_or_failed_load(mock_config_loader_load, caplog):
    """Test __init__ when ConfigLoader.load returns an empty dict (file empty/error)."""
    mock_config_loader_load.return_value = {} # Simulate empty or failed load by ConfigLoader

    manager = FingerprintManager(filepath="empty_fp.json")

    assert manager.fingerprints == []
    assert "Failed to load fingerprints from 'empty_fp.json'" in caplog.text # Checks for the warning

# --- Tests for get_fingerprint ---

def test_get_fingerprint_with_available_fingerprints():
    """Test get_fingerprint when fingerprints are available."""
    initial_fingerprints = ["FP_A", "FP_B", "FP_C"]
    manager = FingerprintManager(fingerprints=initial_fingerprints)

    # Call multiple times, check if returned fingerprint is one of the available ones
    for _ in range(10): # Call it a few times
        fp = manager.get_fingerprint()
        assert fp in initial_fingerprints

def test_get_fingerprint_no_available_fingerprints(caplog):
    """Test get_fingerprint when no fingerprints are available."""
    manager = FingerprintManager(fingerprints=[]) # Initialize with no fingerprints
    assert manager.get_fingerprint() is None
    assert "no fingerprints available" in caplog.text
    caplog.clear()

    # Also test when initialized via (mocked) empty JSON load
    mock_config_loader_load_fixture = mock.Mock(return_value={}) # Create a new mock for this specific case
    with mock.patch('core.config_loader.ConfigLoader.load', new=mock_config_loader_load_fixture):
        manager2 = FingerprintManager(filepath="empty_again.json")
        assert manager2.get_fingerprint() is None
        assert "no fingerprints available" in caplog.text

def test_get_fingerprint_single_fingerprint():
    """Test get_fingerprint when only one fingerprint is available."""
    single_fp_list = ["ONLY_ONE_FP"]
    manager = FingerprintManager(fingerprints=single_fp_list)
    assert manager.get_fingerprint() == "ONLY_ONE_FP"
    # Calling it again should still return the same one
    assert manager.get_fingerprint() == "ONLY_ONE_FP"
