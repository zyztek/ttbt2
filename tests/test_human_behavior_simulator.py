"""
Unit tests for the HumanBehaviorSimulator class in core.evasion.
"""
import pytest
from unittest import mock
import time # For time.sleep, even if mocked
import random # For random.uniform, random.randint, random.random
from core.evasion import HumanBehaviorSimulator
from config import settings # To access BEHAVIOR_PROFILES for expected values

# Mock Selenium WebElement that can be passed to methods needing an element
@pytest.fixture
def mock_web_element():
    """Provides a mock Selenium WebElement."""
    element = mock.Mock()
    element.send_keys = mock.Mock()
    element.click = mock.Mock()
    return element

@pytest.fixture
def mock_driver():
    """Provides a mock Selenium WebDriver."""
    driver = mock.Mock()
    driver.execute_script = mock.Mock()
    return driver

# --- Test __init__ Parameter Loading ---
@pytest.mark.parametrize("mode_name, expected_profile_key", [
    ("safe", "safe"),
    ("balanced", "balanced"),
    ("aggressive", "aggressive"),
    ("unknown_mode", settings.DEFAULT_BOT_MODE) # Test fallback to default
])
def test_init_parameter_loading(mock_driver, mode_name, expected_profile_key, caplog):
    """
    Tests that HumanBehaviorSimulator correctly loads behavioral parameters
    from config.settings.BEHAVIOR_PROFILES based on the provided mode.
    """
    profile = settings.BEHAVIOR_PROFILES[expected_profile_key]
    simulator = HumanBehaviorSimulator(driver=mock_driver, mode=mode_name)

    if mode_name == "unknown_mode":
        assert f"Mode 'unknown_mode' not found in BEHAVIOR_PROFILES. Using default mode '{settings.DEFAULT_BOT_MODE}'." in caplog.text
        assert simulator.mode == settings.DEFAULT_BOT_MODE # Mode should be updated to default
    else:
        assert simulator.mode == mode_name

    assert simulator.current_delay_multiplier == profile["delay_multiplier"]
    assert simulator.current_typing_delay_min == profile["typing_delay_range_secs"][0]
    assert simulator.current_typing_delay_max == profile["typing_delay_range_secs"][1]
    assert simulator.current_space_pause_chance == profile["space_pause_chance"]
    assert simulator.current_space_pause_min_duration == profile["space_pause_duration_range_secs"][0]
    assert simulator.current_space_pause_max_duration == profile["space_pause_duration_range_secs"][1]
    assert simulator.current_video_watch_min == profile["video_watch_time_range_secs"][0]
    assert simulator.current_video_watch_max == profile["video_watch_time_range_secs"][1]
    assert simulator.current_click_min_delay == profile["click_base_delay_range_secs"][0]
    assert simulator.current_click_max_delay == profile["click_base_delay_range_secs"][1]
    assert simulator.current_scroll_min_pixels == profile["scroll_amount_range_pixels"][0]
    assert simulator.current_scroll_max_pixels == profile["scroll_amount_range_pixels"][1]
    assert simulator.current_scroll_pause_min == profile["scroll_pause_duration_range_secs"][0]
    assert simulator.current_scroll_pause_max == profile["scroll_pause_duration_range_secs"][1]

# --- Test random_delay() ---
@mock.patch('time.sleep') # Mock time.sleep to check its calls
@mock.patch('random.uniform') # Mock random.uniform to control its return value
def test_random_delay_logic(mock_uniform, mock_sleep, mock_driver):
    """Tests the logic of random_delay, including mode multiplier and clamping."""
    # Test with 'safe' mode (multiplier 1.5 from settings)
    simulator_safe = HumanBehaviorSimulator(driver=mock_driver, mode="safe")
    mock_uniform.return_value = 2.25 # Mocked sleep duration
    simulator_safe.random_delay(min_seconds=1.0, max_seconds=2.0)
    # Expected: adj_min = 1.0 * 1.5 = 1.5, adj_max = 2.0 * 1.5 = 3.0
    mock_uniform.assert_called_once_with(1.5, 3.0)
    mock_sleep.assert_called_once_with(2.25)
    mock_uniform.reset_mock()
    mock_sleep.reset_mock()

    # Test with 'aggressive' mode (multiplier 0.7 from settings)
    simulator_aggressive = HumanBehaviorSimulator(driver=mock_driver, mode="aggressive")
    mock_uniform.return_value = 0.49
    simulator_aggressive.random_delay(min_seconds=0.5, max_seconds=1.0)
    # Expected: adj_min = 0.5 * 0.7 = 0.35, adj_max = 1.0 * 0.7 = 0.7
    mock_uniform.assert_called_once_with(0.35, 0.7)
    mock_sleep.assert_called_once_with(0.49)
    mock_uniform.reset_mock()
    mock_sleep.reset_mock()

    # Test clamping logic: adj_min < 0.01
    # Using balanced mode (multiplier 1.0) for simplicity here
    simulator_balanced = HumanBehaviorSimulator(driver=mock_driver, mode="balanced")
    mock_uniform.return_value = 0.01 # Expected sleep after clamping
    simulator_balanced.random_delay(min_seconds=0.001, max_seconds=0.005)
    # Expected: adj_min clamped to 0.01, adj_max becomes 0.01 + 0.01 = 0.02
    mock_uniform.assert_called_once_with(0.01, 0.02)
    mock_sleep.assert_called_once_with(0.01)
    mock_uniform.reset_mock()
    mock_sleep.reset_mock()

    # Test clamping logic: adj_min >= adj_max after multiplication
    # E.g. very small range with aggressive multiplier
    # multiplier for aggressive is 0.7
    # min_seconds = 0.02 -> 0.014 (clamped to 0.01)
    # max_seconds = 0.01 -> 0.007 (but adj_max must be > adj_min)
    mock_uniform.return_value = 0.01 # Expected sleep after clamping
    simulator_aggressive.random_delay(min_seconds=0.02, max_seconds=0.01)
    # Expected: adj_min = 0.02 * 0.7 = 0.014 (clamped to 0.01)
    # adj_max = 0.01 * 0.7 = 0.007. Since adj_min (0.01) > adj_max (0.007), adj_max = adj_min + 0.01 = 0.02
    mock_uniform.assert_called_once_with(0.01, 0.02)
    mock_sleep.assert_called_once_with(0.01)


# --- Test human_type() ---
@mock.patch('time.sleep')
@mock.patch('random.uniform') # To control standard character delay
@mock.patch('random.random') # To control space pause chance
def test_human_type_delays_and_space_pause(mock_random_chance, mock_uniform_delay, mock_sleep, mock_driver, mock_web_element):
    """Tests human_type for correct character delays and space pause logic."""
    simulator = HumanBehaviorSimulator(driver=mock_driver, mode="safe") # Safe mode has space pause chance

    # Mock standard character delay
    char_delay_val = (settings.BEHAVIOR_PROFILES["safe"]["typing_delay_range_secs"][0] +
                      settings.BEHAVIOR_PROFILES["safe"]["typing_delay_range_secs"][1]) / 2
    mock_uniform_delay.return_value = char_delay_val

    # Scenario 1: Special space pause IS triggered
    mock_random_chance.return_value = 0.01 # Lower than safe mode's space_pause_chance (0.10)

    # Mock simulator.random_delay which is used for space pause
    # We need to mock it on the instance because it's a method of the class being tested.
    with mock.patch.object(simulator, 'random_delay') as mock_instance_random_delay:
        simulator.human_type(mock_web_element, "a b")

        # Check send_keys calls
        calls = [mock.call('a'), mock.call(' '), mock.call('b')]
        mock_web_element.send_keys.assert_has_calls(calls)

        # Check sleep/delay calls
        # After 'a': standard char delay
        mock_uniform_delay.assert_any_call(simulator.current_typing_delay_min, simulator.current_typing_delay_max)
        # After ' ': special space pause (via simulator.random_delay)
        mock_instance_random_delay.assert_called_once_with(
            simulator.current_space_pause_min_duration,
            simulator.current_space_pause_max_duration
        )
        # After 'b': standard char delay (mock_sleep would be called directly by time.sleep)
        # Total mock_sleep calls: after 'a', and after 'b'
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(char_delay_val)


    # Reset mocks for Scenario 2
    mock_web_element.reset_mock()
    mock_sleep.reset_mock()
    mock_uniform_delay.reset_mock()
    mock_random_chance.reset_mock()

    # Scenario 2: Special space pause IS NOT triggered
    mock_random_chance.return_value = 0.99 # Higher than space_pause_chance
    mock_uniform_delay.return_value = char_delay_val # Re-set return value

    with mock.patch.object(simulator, 'random_delay') as mock_instance_random_delay_2:
        simulator.human_type(mock_web_element, "c d")

        calls_2 = [mock.call('c'), mock.call(' '), mock.call('d')]
        mock_web_element.send_keys.assert_has_calls(calls_2)

        # After ' ': standard char delay because random_chance was high
        # simulator.random_delay should NOT have been called for the space
        mock_instance_random_delay_2.assert_not_called()

        # All delays should be standard character delays
        assert mock_uniform_delay.call_count == 3 # after 'c', after ' ', after 'd'
        assert mock_sleep.call_count == 3


# --- Test human_click() ---
def test_human_click_uses_profile_delays(mock_driver, mock_web_element):
    """Tests that human_click uses click delay ranges from the profile."""
    simulator = HumanBehaviorSimulator(driver=mock_driver, mode="aggressive") # Aggressive has specific click delays

    # Mock the random_delay method on this instance
    with mock.patch.object(simulator, 'random_delay') as mock_instance_random_delay:
        simulator.human_click(mock_web_element)

        mock_web_element.click.assert_called_once()

        # Check that random_delay was called twice with the aggressive mode's click delays
        expected_min = settings.BEHAVIOR_PROFILES["aggressive"]["click_base_delay_range_secs"][0]
        expected_max = settings.BEHAVIOR_PROFILES["aggressive"]["click_base_delay_range_secs"][1]

        calls = [mock.call(expected_min, expected_max), mock.call(expected_min, expected_max)]
        mock_instance_random_delay.assert_has_calls(calls)
        assert mock_instance_random_delay.call_count == 2


# --- Test watch_video() ---
def test_watch_video_uses_profile_delays(mock_driver):
    """Tests that watch_video uses video watch time ranges from the profile."""
    simulator = HumanBehaviorSimulator(driver=mock_driver, mode="safe") # Safe mode has specific watch times

    with mock.patch.object(simulator, 'random_delay') as mock_instance_random_delay:
        simulator.watch_video()

        expected_min = settings.BEHAVIOR_PROFILES["safe"]["video_watch_time_range_secs"][0]
        expected_max = settings.BEHAVIOR_PROFILES["safe"]["video_watch_time_range_secs"][1]
        mock_instance_random_delay.assert_called_once_with(expected_min, expected_max)

# --- Test random_scroll() ---
@mock.patch('random.randint')
def test_random_scroll_uses_profile_params(mock_randint, mock_driver):
    """Tests that random_scroll uses scroll parameters from the profile."""
    simulator = HumanBehaviorSimulator(driver=mock_driver, mode="balanced") # Balanced mode

    # Mock random.randint to control scroll amount
    expected_scroll_amount = 450
    mock_randint.return_value = expected_scroll_amount

    with mock.patch.object(simulator, 'random_delay') as mock_instance_random_delay:
        simulator.random_scroll()

        # Check scroll amount
        min_scroll = settings.BEHAVIOR_PROFILES["balanced"]["scroll_amount_range_pixels"][0]
        max_scroll = settings.BEHAVIOR_PROFILES["balanced"]["scroll_amount_range_pixels"][1]
        mock_randint.assert_called_once_with(min_scroll, max_scroll)
        mock_driver.execute_script.assert_called_once_with(f"window.scrollBy(0, {expected_scroll_amount});")

        # Check scroll pause duration
        expected_min_pause = settings.BEHAVIOR_PROFILES["balanced"]["scroll_pause_duration_range_secs"][0]
        expected_max_pause = settings.BEHAVIOR_PROFILES["balanced"]["scroll_pause_duration_range_secs"][1]
        mock_instance_random_delay.assert_called_once_with(expected_min_pause, expected_max_pause)

# Placeholder tests for like_video (as it currently just logs and has a placeholder selector)
def test_like_video_logs_and_attempts_placeholder_click(mock_driver, mock_web_element, caplog):
    """Tests that like_video logs appropriately and attempts to click a placeholder."""
    # To make find_element work, we need the driver to return our mock_web_element
    mock_driver.find_element.return_value = mock_web_element

    simulator = HumanBehaviorSimulator(driver=mock_driver, mode="balanced")

    # Mock human_click on this instance to avoid its internal delays during this test
    with mock.patch.object(simulator, 'human_click') as mock_human_click:
        simulator.like_video()

        assert f"Attempting to find like button with placeholder XPath: {simulator.LIKE_BUTTON_SELECTOR_XPATH_PLACEHOLDER}" in caplog.text
        mock_driver.find_element.assert_called_once_with(By.XPATH, simulator.LIKE_BUTTON_SELECTOR_XPATH_PLACEHOLDER)
        mock_human_click.assert_called_once_with(mock_web_element)
        assert "Placeholder like button clicked successfully." in caplog.text # Assuming find_element and click succeed

def test_like_video_handles_find_failure(mock_driver, caplog):
    """Tests that like_video handles failure to find the placeholder button."""
    mock_driver.find_element.side_effect = Exception("Element not found (simulated)") # Simulate find_element failure

    simulator = HumanBehaviorSimulator(driver=mock_driver, mode="balanced")

    with mock.patch.object(simulator, 'human_click') as mock_human_click: # human_click shouldn't be called
        simulator.like_video()

        assert "Could not click placeholder like button" in caplog.text
        mock_human_click.assert_not_called()

# It's good practice to import By for this test, even if HumanBehaviorSimulator imports it.
from selenium.webdriver.common.by import By
