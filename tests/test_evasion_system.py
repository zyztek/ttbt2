import unittest
from unittest import mock

from core.evasion_system import EvasionSystem

class TestEvasionSystem(unittest.TestCase):

    def setUp(self):
        self.mock_driver = mock.Mock()
        self.evasion_system = EvasionSystem(self.mock_driver)

    def test_evade_detection_applies_webdriver_trick(self):
        self.evasion_system.evade_detection()
        self.mock_driver.execute_script.assert_called_once_with(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

    def test_init_stores_driver(self):
        assert self.evasion_system.driver == self.mock_driver # Changed to pytest style

    @mock.patch('builtins.print')
    def test_evade_detection_driver_execute_raises_exception(self, mock_print):
        self.mock_driver.execute_script.side_effect = Exception("Simulated JS error")

        self.evasion_system.evade_detection()

        self.mock_driver.execute_script.assert_called_once_with(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        # Check if the specific error message was printed
        error_message_found = False
        for call_args in mock_print.call_args_list:
            if "[EVASION_SYSTEM] Error applying webdriver hiding trick: Simulated JS error" in call_args[0][0]:
                error_message_found = True
                break
        assert error_message_found, "Expected JS error message not printed."

    @mock.patch('builtins.print')
    def test_evade_detection_no_driver(self, mock_print):
        ev_sys_no_driver = EvasionSystem(None)
        ev_sys_no_driver.evade_detection()
        mock_print.assert_called_once_with("[EVASION_SYSTEM] No driver available to apply evasion techniques.")

if __name__ == '__main__':
    unittest.main()
