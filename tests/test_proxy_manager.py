"""
Unit tests for the ProxyManager class in proxies.proxy_manager.
"""
import pytest
from unittest import mock
from proxies.proxy_manager import ProxyManager
# Logger from the module being tested to check its output
from proxies.proxy_manager import proxy_manager_logger as manager_logger

@pytest.fixture
def mock_config_loader_load(mocker):
    """
    Pytest fixture to mock core.config_loader.ConfigLoader.load.
    This prevents actual file I/O during tests and allows controlled return values.
    """
    return mocker.patch('core.config_loader.ConfigLoader.load')

# --- Tests for __init__ ---

def test_init_direct_list():
    """Test __init__ with a directly provided list of proxies."""
    direct_proxies = ["http://proxy1.com:8080", "http://proxy2.com:8000"]
    manager = ProxyManager(proxies=direct_proxies, filepath="dummy_path.json") # filepath won't be used

    assert manager.proxies == direct_proxies
    assert manager.active_proxies == set(direct_proxies)
    # No call to ConfigLoader.load should have been made if proxies list is passed

def test_init_load_from_json_success(mock_config_loader_load, caplog):
    """Test __init__ with successful loading of proxies from JSON."""
    mock_data = {"proxies": ["http://json_proxy1.com", "http://json_proxy2.com"]}
    mock_config_loader_load.return_value = mock_data

    manager = ProxyManager(filepath="valid_proxies.json") # proxies=None by default

    assert manager.proxies == mock_data["proxies"]
    assert manager.active_proxies == set(mock_data["proxies"])
    mock_config_loader_load.assert_called_once_with("valid_proxies.json")
    assert f"Successfully loaded {len(mock_data['proxies'])} proxies" in caplog.text

def test_init_load_from_json_malformed_data(mock_config_loader_load, caplog):
    """Test __init__ when JSON data is malformed (e.g., missing 'proxies' key or not a list)."""
    # Case 1: 'proxies' key missing
    mock_config_loader_load.return_value = {"other_key": ["data"]}
    manager = ProxyManager(filepath="malformed1.json")
    assert manager.proxies == []
    assert manager.active_proxies == set()
    assert "Failed to load proxies from 'malformed1.json'" in caplog.text
    caplog.clear()

    # Case 2: 'proxies' is not a list
    mock_config_loader_load.return_value = {"proxies": "this_should_be_a_list"}
    manager2 = ProxyManager(filepath="malformed2.json")
    assert manager2.proxies == []
    assert manager2.active_proxies == set()
    assert "Failed to load proxies from 'malformed2.json'" in caplog.text
    caplog.clear()

    # Case 3: Loaded data is not a dictionary
    mock_config_loader_load.return_value = ["just_a_list_not_dict"]
    manager3 = ProxyManager(filepath="malformed3.json")
    assert manager3.proxies == []
    assert manager3.active_proxies == set()
    assert "Failed to load proxies from 'malformed3.json'" in caplog.text


def test_init_load_from_json_empty_or_failed_load(mock_config_loader_load, caplog):
    """Test __init__ when ConfigLoader.load returns an empty dict (file empty/error)."""
    mock_config_loader_load.return_value = {} # Simulate empty or failed load by ConfigLoader

    manager = ProxyManager(filepath="empty.json")

    assert manager.proxies == []
    assert manager.active_proxies == set()
    assert "Failed to load proxies from 'empty.json'" in caplog.text # Checks for the warning

# --- Tests for get_random_active_proxy ---

def test_get_random_active_proxy_with_active_proxies():
    """Test get_random_active_proxy when active proxies are available."""
    initial_proxies = ["p1", "p2", "p3"]
    manager = ProxyManager(proxies=initial_proxies)

    # Call multiple times, check if returned proxy is one of the active ones
    for _ in range(10): # Call it a few times
        proxy = manager.get_random_active_proxy()
        assert proxy in initial_proxies

def test_get_random_active_proxy_no_active_proxies(caplog):
    """Test get_random_active_proxy when no active proxies are available."""
    manager = ProxyManager(proxies=[]) # Initialize with no proxies
    assert manager.get_random_active_proxy() is None
    assert "no active proxies available" in caplog.text
    caplog.clear()

    # Test after deactivating all
    manager2 = ProxyManager(proxies=["p1", "p2"])
    manager2.deactivate_proxy("p1")
    manager2.deactivate_proxy("p2")
    assert manager2.get_random_active_proxy() is None
    assert "no active proxies available" in caplog.text

# --- Tests for deactivate_proxy ---

def test_deactivate_proxy_existing(caplog):
    """Test deactivating an existing proxy."""
    initial_proxies = ["p1", "p2", "p3"]
    manager = ProxyManager(proxies=initial_proxies)

    manager.deactivate_proxy("p2")
    assert "p2" not in manager.active_proxies
    assert manager.active_proxies == {"p1", "p3"}
    assert manager.proxies == initial_proxies # Original list should be unchanged
    assert "Proxy deactivated: p2" in caplog.text
    assert f"Remaining active proxies: {len(manager.active_proxies)}" in caplog.text

def test_deactivate_proxy_non_existing(caplog):
    """Test deactivating a proxy that is not in the active set."""
    initial_proxies = ["p1", "p2"]
    manager = ProxyManager(proxies=initial_proxies)

    manager.deactivate_proxy("p3") # p3 is not in active_proxies
    assert manager.active_proxies == {"p1", "p2"} # Set should be unchanged
    assert "Attempted to deactivate proxy not in active set: p3" in caplog.text

def test_deactivate_all_then_get(caplog):
    """Test deactivating all proxies and then trying to get one."""
    proxies = ["p1", "p2"]
    manager = ProxyManager(proxies=proxies)

    manager.deactivate_proxy("p1")
    manager.deactivate_proxy("p2")

    assert len(manager.active_proxies) == 0
    assert manager.get_random_active_proxy() is None
    assert "no active proxies available" in caplog.text
