import unittest
from unittest import mock
import time # Required for time.sleep if we test its call count/duration

from core.behavior import HumanBehaviorSimulator

class TestHumanBehaviorSimulator(unittest.TestCase):

    def setUp(self):
        self.mock_driver = mock.Mock()
        self.simulator = HumanBehaviorSimulator(self.mock_driver)

    @mock.patch('time.sleep', return_value=None) # Mock time.sleep
    def test_human_type(self, mock_sleep):
        mock_element = mock.Mock()
        test_text = "hello"
        self.simulator.human_type(mock_element, test_text)

        # Check if send_keys was called for each character
        calls = [mock.call(char) for char in test_text]
        mock_element.send_keys.assert_has_calls(calls, any_order=False)
        self.assertEqual(mock_sleep.call_count, len(test_text))

    def test_human_click(self):
        mock_element = mock.Mock()
        self.simulator.human_click(mock_element)
        mock_element.click.assert_called_once()

    @mock.patch('time.sleep', return_value=None) # Mock time.sleep for random_delay
    @mock.patch('random.randint', return_value=500) # Mock random.randint
    def test_random_scroll(self, mock_randint, mock_sleep):
        self.simulator.random_scroll()
        self.mock_driver.execute_script.assert_called_once_with("window.scrollBy(0, 500);")
        # random_scroll also calls self.random_delay(1,3)
        # Ensure random_delay's time.sleep was called (it's mocked at method level)
        # The number of calls to mock_sleep would be 1 from random_delay
        self.assertTrue(mock_sleep.called)

    @mock.patch.object(HumanBehaviorSimulator, 'random_delay') # Mock a method of the class
    def test_watch_video(self, mock_random_delay):
        self.simulator.watch_video()
        # Check that random_delay was called with balanced mode video_watch_time_range_secs (5, 15)
        mock_random_delay.assert_called_once_with(5, 15)

    @mock.patch.object(HumanBehaviorSimulator, 'random_delay') # Mock random_delay
    def test_like_video_success(self, mock_random_delay):
        mock_like_button = mock.Mock()
        self.mock_driver.find_element.return_value = mock_like_button

        self.simulator.like_video()

        self.mock_driver.find_element.assert_called_once_with(
            "xpath", # Using xpath string as expected by the method
            "//button[@data-testid='like-button-placeholder']"
        )
        mock_like_button.click.assert_called_once()
        # human_click calls random_delay twice (pre and post-click) with click_base_delay_range_secs
        # For balanced mode, this is (0.2, 0.5)
        assert mock_random_delay.call_count == 2
        mock_random_delay.assert_has_calls([
            mock.call(0.2, 0.5),  # pre-click delay
            mock.call(0.2, 0.5)   # post-click delay
        ])

    @mock.patch.object(HumanBehaviorSimulator, 'random_delay') # Mock random_delay
    def test_like_video_failure_no_button(self, mock_random_delay):
        # Simulate find_element raising an exception (e.g., NoSuchElementException)
        self.mock_driver.find_element.side_effect = Exception("Element not found")

        self.simulator.like_video() # Should not raise an error due to try-except

        self.mock_driver.find_element.assert_called_once_with(
            "xpath",
            "//button[@data-testid='like-button-placeholder']"
        )
        # click() should not have been called on the button
        # random_delay should not have been called if it failed before that
        mock_random_delay.assert_not_called()

    @mock.patch('time.sleep', return_value=None)
    def test_random_delay_min_greater_than_max(self, mock_sleep):
        """Test random_delay when min >= max due to multiplier adjustment."""
        # Create a behavior simulator with extreme multiplier to trigger the edge case
        simulator = HumanBehaviorSimulator(self.mock_driver, mode='safe')
        simulator.current_delay_multiplier = 0.0001  # Very small multiplier
        
        with mock.patch('random.uniform') as mock_uniform:
            mock_uniform.return_value = 0.015
            # Call with values that when multiplied by 0.0001 will be very small
            # This will trigger the adj_min >= adj_max condition 
            simulator.random_delay(100, 110)
            # Check that adj_max was adjusted to be greater than adj_min
            mock_uniform.assert_called_once()
            args = mock_uniform.call_args[0]
            assert args[1] > args[0]  # Ensure max > min
                
    @mock.patch('time.sleep', return_value=None)
    def test_human_type_with_space_no_pause(self, mock_sleep):
        """Test human_type when space doesn't trigger special pause."""
        element = mock.Mock()
        text = "hello world"
        
        # Mock random to always return a value that doesn't trigger space pause
        with mock.patch('random.random', return_value=0.9):  # > space_pause_chance
            with mock.patch('random.uniform', return_value=0.05) as mock_uniform:
                self.simulator.human_type(element, text)
                
                # Verify the element received all characters
                expected_calls = [mock.call(char) for char in text]
                element.send_keys.assert_has_calls(expected_calls)
                
                # Should have been called for each character with typing delay
                assert mock_uniform.call_count == len(text)
                    
    @mock.patch('time.sleep', return_value=None)
    def test_human_type_with_space_pause(self, mock_sleep):
        """Test human_type when space triggers special pause."""
        element = mock.Mock()
        text = "hello world"
        
        # Mock random to trigger space pause for space character
        with mock.patch('random.random', return_value=0.1):  # < space_pause_chance
            with mock.patch.object(self.simulator, 'random_delay') as mock_random_delay:
                with mock.patch('random.uniform', return_value=0.05) as mock_uniform:
                    self.simulator.human_type(element, text)
                    
                    # Should have called random_delay for the space character
                    mock_random_delay.assert_called_with(
                        self.simulator.current_space_pause_min_duration,
                        self.simulator.current_space_pause_max_duration
                    )

if __name__ == '__main__':
    unittest.main()
