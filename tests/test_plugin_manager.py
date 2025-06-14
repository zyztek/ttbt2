from core.plugin_manager import PluginManager
import os # Added
from unittest import mock # Added

def test_plugin_manager_load_and_execute(tmp_path):
    plugin_code = "def after_login(bot): bot.test_value = 42"
    plugin_path = tmp_path / "test_plugin.py"
    plugin_path.write_text(plugin_code)
    pm = PluginManager()
    pm.load_plugin(str(plugin_path))

    class DummyBot:
        pass

    bot = DummyBot()
    pm.execute_hook("after_login", bot=bot)
    assert bot.test_value == 42

def test_load_plugin_file_not_found(tmp_path):
    pm = PluginManager()
    non_existent_plugin_path = tmp_path / "non_existent_plugin.py"

    # Ensure os.path.isfile is mocked if direct file system check is an issue,
    # or rely on the fact that the file truly doesn't exist.
    # For robustness with mocks:
    with mock.patch('core.plugin_manager.os.path.isfile', return_value=False) as mock_isfile:
        pm.load_plugin(str(non_existent_plugin_path))
        mock_isfile.assert_called_once_with(str(non_existent_plugin_path))

    assert pm.hooks == {} # No hooks should be loaded

def test_execute_hook_not_found(tmp_path):
    pm = PluginManager()
    # Create and load a dummy plugin to ensure hooks dict is not empty from other sources
    plugin_code = "def existing_hook(): pass"
    plugin_path = tmp_path / "dummy_plugin_for_hook_test.py"
    plugin_path.write_text(plugin_code)
    pm.load_plugin(str(plugin_path)) # Load some valid hook

    result = pm.execute_hook("non_existent_hook_name")
    assert result is None # Should return None if hook is not found

    # Ensure existing_hook is there to prove the dict wasn't empty
    assert "existing_hook" in pm.hooks