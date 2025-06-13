# tests/test_main_script.py
import os
import json
import tempfile
import shutil
import pytest # Ensure pytest is imported if used directly for fixtures/raises
from unittest import mock
import argparse # Should be from main, or mocked if testing main.parse_args standalone
import sys # For sys.argv and sys.exit mocking
import builtins # For print mocking

# Assuming main.py is in root and core is accessible
# This import might need to be within test functions if main itself is modified by runpy
import main

# Dummy definitions if not imported from elsewhere, for tests that need them
# class DummyProxyManager:
#     def get_random_active_proxy(self): return "proxyZ"
# class DummyFingerprintManager:
#     def get_fingerprint(self): return "fpW"

def create_temp_file(directory, filename, content):
    path = os.path.join(directory, filename)
    # Ensure content is string if opening in text mode, or open in binary if content is bytes
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f)
    return path

@pytest.fixture
def temp_env(): # Renamed from temp_env_for_main for consistency if this is the only one
    base_dir = tempfile.mkdtemp()
    proxies_dir = os.path.join(base_dir, "proxies")
    fingerprints_dir = os.path.join(base_dir, "fingerprints")
    os.makedirs(proxies_dir, exist_ok=True)
    os.makedirs(fingerprints_dir, exist_ok=True)

    # Create a dummy accounts.json as TikTokBot instantiates AccountManager
    # which might try to load a default file if not given a path.
    # main.py's TikTokBot() call doesn't pass a path to AccountManager.
    create_temp_file(base_dir, "accounts.json", {"dummy_user": {"password": "dummy_password"}})

    yield base_dir # Provide just the base_dir as the fixture value
    shutil.rmtree(base_dir)

# Tests for main.parse_args()
def test_parse_args_defaults():
    # Temporarily clear sys.argv or pass specific args for parse_args
    with mock.patch.object(sys, 'argv', ['main.py']):
        args = main.parse_args()
    assert args.mode == "balanced"
    assert args.max_views == 5000

def test_parse_args_custom():
    with mock.patch.object(sys, 'argv', ['main.py', '--mode', 'aggressive', '--max-views', '100']):
        args = main.parse_args()
    assert args.mode == "aggressive"
    assert args.max_views == 100

# Tests for main.main_script_logic(args)
@mock.patch('main.Thread')
@mock.patch('main.app.run') # Mock Flask app.run
@mock.patch('main.TikTokBot')
def test_main_script_execution_success(mock_tiktok_bot, mock_app_run, mock_thread, temp_env, monkeypatch):
    base_dir = temp_env # Use the fixture
    monkeypatch.chdir(base_dir) # Change current working directory to temp_dir

    mock_bot_instance = mock.MagicMock()
    mock_bot_instance.driver = mock.MagicMock() # Ensure driver is not None
    mock_tiktok_bot.return_value = mock_bot_instance

    # Mock args that would come from parse_args()
    mock_args = argparse.Namespace(mode="test_mode", max_views=123)

    with mock.patch.dict(os.environ, {}, clear=True): # Clear os.environ for predictable test
         main.main_script_logic(mock_args)

    mock_tiktok_bot.assert_called_once_with()
    mock_bot_instance.run_session.assert_called_once()
    mock_bot_instance.driver.quit.assert_called_once() # From finally block
    assert os.environ["MAX_VIEWS_PER_HOUR"] == "123"

    # Check Flask thread
    mock_thread.assert_called_once_with(target=main.run_flask)
    mock_thread.return_value.start.assert_called_once()


@mock.patch('builtins.print')
@mock.patch('sys.exit') # Mock sys.exit
@mock.patch('main.Thread') # Mock Thread to prevent it from starting
@mock.patch('main.app.run') # Mock Flask app.run
@mock.patch('main.TikTokBot')
def test_main_script_bot_driver_failure(mock_tiktok_bot, mock_app_run, mock_thread, mock_sys_exit, mock_print, temp_env, monkeypatch):
    base_dir = temp_env
    monkeypatch.chdir(base_dir)

    mock_bot_instance = mock.MagicMock()
    mock_bot_instance.driver = None # Simulate driver initialization failure
    mock_tiktok_bot.return_value = mock_bot_instance

    mock_args = argparse.Namespace(mode="test_mode", max_views=456)

    # Configure sys.exit to raise an exception that can be caught by pytest.raises
    mock_sys_exit.side_effect = SystemExit(1)

    with pytest.raises(SystemExit) as e_info:
        main.main_script_logic(mock_args)

    assert e_info.value.code == 1
    mock_tiktok_bot.assert_called_once_with()
    mock_print.assert_any_call("Failed to initialize bot - Chrome driver not available")
    mock_sys_exit.assert_called_once_with(1)

    # Ensure Flask part is not reached
    mock_thread.assert_not_called()


@mock.patch('main.app.run')
def test_run_flask_uses_env_host(mock_app_run):
    with mock.patch.dict(os.environ, {'FLASK_HOST': '0.0.0.0'}): # Use clear=True if needed
        main.run_flask()
    mock_app_run.assert_called_once_with(host='0.0.0.0', port=5000)

@mock.patch('main.app.run')
def test_run_flask_uses_default_host(mock_app_run):
    # Ensure FLASK_HOST is not set for this test
    with mock.patch.dict(os.environ, {}, clear=True):
        main.run_flask()
    mock_app_run.assert_called_once_with(host='127.0.0.1', port=5000)


@mock.patch('builtins.print')
@mock.patch('main.Thread') # Mock Thread to prevent it from starting
@mock.patch('main.app.run') # Mock Flask app.run
@mock.patch('main.TikTokBot')
def test_main_script_logic_run_session_exception(mock_tiktok_bot, mock_app_run, mock_thread, mock_print, temp_env, monkeypatch):
    base_dir = temp_env
    monkeypatch.chdir(base_dir)

    mock_bot_instance = mock.MagicMock()
    mock_bot_instance.driver = mock.MagicMock() # Driver exists
    mock_bot_instance.run_session.side_effect = Exception("Test_Session_Exception")
    mock_tiktok_bot.return_value = mock_bot_instance

    mock_args = argparse.Namespace(mode="test_mode", max_views=10)

    main.main_script_logic(mock_args)

    mock_print.assert_any_call("Error crítico: Test_Session_Exception")
    mock_bot_instance.driver.quit.assert_called_once() # Should still be called in finally
    mock_print.assert_any_call("Sesión de bot principal finalizada.")
    mock_thread.assert_called_once() # Flask should still start


@mock.patch('builtins.print')
@mock.patch('main.Thread') # Mock Thread
@mock.patch('main.app.run') # Mock Flask
@mock.patch('main.TikTokBot')
def test_main_script_logic_driver_quit_exception(mock_tiktok_bot, mock_app_run, mock_thread, mock_print, temp_env, monkeypatch):
    base_dir = temp_env
    monkeypatch.chdir(base_dir)

    mock_bot_instance = mock.MagicMock()
    mock_bot_instance.driver = mock.MagicMock() # Driver exists
    mock_bot_instance.driver.quit.side_effect = Exception("Test_Quit_Exception")
    mock_tiktok_bot.return_value = mock_bot_instance

    mock_args = argparse.Namespace(mode="test_mode", max_views=10)

    main.main_script_logic(mock_args)

    mock_bot_instance.driver.quit.assert_called_once()
    mock_print.assert_any_call("Error closing driver: Test_Quit_Exception")
    mock_print.assert_any_call("Sesión de bot principal finalizada.")
    mock_thread.assert_called_once() # Flask should still start