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
    @mock.patch('random.uniform', return_value=15.0) # Mock random.uniform used by watch_video
    def test_watch_video(self, mock_uniform, mock_random_delay):
        self.simulator.watch_video()
        # Check that random_delay was called with the value from random.uniform
        mock_random_delay.assert_called_once_with(15.0, 15.0)

    def test_like_video(self):
        # Test that it runs without error and potentially prints (if we capture stdout)
        # For now, just ensure it can be called.
        try:
            self.simulator.like_video()
        except Exception as e:
            self.fail(f"like_video raised an exception {e}")
        # If we wanted to check print output:
        # with mock.patch('builtins.print') as mock_print:
        #     self.simulator.like_video()
        #     mock_print.assert_called_with("[SIM_BEHAVIOR] 'Liking video'.")

if __name__ == '__main__':
    unittest.main()
