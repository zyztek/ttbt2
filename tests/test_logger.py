import unittest
from unittest import mock
import os
import importlib # Added for reloading

# To allow the test module to load core.logger, core.logger needs to be importable.
# We'll mock loguru at the top level for all tests in this module
# as its setup is global in core/logger.py

mock_loguru_logger = mock.MagicMock()

# Define a fake 'add' method for our mock_loguru_logger
# that we can inspect later if needed. For now, just making it exist.
# mock_loguru_logger.add = mock.MagicMock()
# mock_loguru_logger.bind = mock.MagicMock(side_effect=lambda name: f"logger_bound_to_{name if name else 'None'}")

# It's better to mock the loguru module itself before core.logger is imported by the test runner
# However, subtasks might not easily support module-level mocks before import for the SUT.
# An alternative: mock specific functions used within core.logger when testing core.logger.

class TestCoreLogger(unittest.TestCase):

    @mock.patch.dict(os.environ, {"LOG_PATH": "custom/path/test.log"})
    @mock.patch("core.logger.os.makedirs") # Mock os.makedirs within core.logger
    @mock.patch("loguru.logger") # Mock loguru.logger directly
    def test_log_path_custom_and_dir_creation(self, mock_loguru_pkg_logger, mock_makedirs):
        # Import core.logger here to ensure mocks are active if it's the first time
        import core.logger
        # Reload core.logger to apply mocks and env var during its import-time execution
        importlib.reload(core.logger)

        # Access the reloaded module's LOG_PATH
        # and the logger instance that was configured during reload
        reloaded_log_path = core.logger.LOG_PATH
        # The mock_loguru_pkg_logger is what 'from loguru import logger' becomes in core.logger

        self.assertEqual(reloaded_log_path, "custom/path/test.log")
        mock_makedirs.assert_called_with(os.path.dirname("custom/path/test.log"), exist_ok=True)

        # Check that the mocked loguru.logger.add was called with the correct path
        mock_loguru_pkg_logger.add.assert_any_call(
            "custom/path/test.log",
            rotation="1 MB",
            retention="7 days",
            level="INFO",
            enqueue=True
        )

    @mock.patch("core.logger.logger") # Mock the module's logger instance
    def test_get_logger_with_name(self, mock_module_logger_instance):
        from core.logger import get_logger # get_logger uses the logger instance from its module

        # Configure the mock's bind method for this test
        mock_module_logger_instance.bind.return_value = "mocked_bound_logger_with_name"

        logger_instance = get_logger("test_module")
        mock_module_logger_instance.bind.assert_called_once_with(name="test_module")
        self.assertEqual(logger_instance, "mocked_bound_logger_with_name")

    @mock.patch("core.logger.logger") # Mock the module's logger instance
    def test_get_logger_without_name(self, mock_module_logger_instance):
        from core.logger import get_logger # get_logger uses the logger instance from its module

        mock_module_logger_instance.bind.return_value = "mocked_bound_logger_no_name"

        logger_instance = get_logger()
        mock_module_logger_instance.bind.assert_called_once_with(name=None)
        self.assertEqual(logger_instance, "mocked_bound_logger_no_name")

    # It's hard to test the logger.add calls without complex module reloading
    # or having core.logger.py be more function-driven for its setup.
    # For now, we'll focus on get_logger and observable side effects if possible.

if __name__ == '__main__':
    unittest.main()
