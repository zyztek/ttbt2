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
        self.assertEqual(self.evasion_system.driver, self.mock_driver)

if __name__ == '__main__':
    unittest.main()
