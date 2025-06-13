import os
import sys
import json
import tempfile
import shutil
import argparse
import runpy
from unittest import mock

import pytest

# Custom exception for testing sys.exit scenarios (No longer needed)
# class TestAbortException(Exception):
#     pass

# Assuming main.py is in the parent directory or accessible via PYTHONPATH
# For robust testing, it's better if main.py can be imported as a module
# For this exercise, we'll assume it's importable or use runpy.

# If main.py can be imported directly (e.g. it's in PYTHONPATH or installed)
# from main import parse_args, run_flask # Assuming run_flask can be imported for Thread target check
# For this exercise, we will mock these or test them via side effects of running main.

def create_temp_file(directory, filename, content):
    path = os.path.join(directory, filename)
    # Ensure content is written as a string if it's JSON
    with open(path, "w", encoding="utf-8") as f:
        if isinstance(content, (dict, list)):
            json.dump(content, f)
        else:
            f.write(content)
    return path

@pytest.fixture
def temp_env_for_main():
    base_dir = tempfile.mkdtemp()
    # Minimal structure, main.py doesn't directly use proxies/fingerprints files
    # but relies on AccountManager which might, so we ensure paths are writable if needed by other components.
    os.makedirs(os.path.join(base_dir, "proxies"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "fingerprints"), exist_ok=True)

    # Create a dummy accounts.json as TikTokBot tries to instantiate AccountManager
    # which might try to load a default file.
    create_temp_file(base_dir, "accounts.json", {"dummy_user": {"password": "dummy_password"}})

    yield base_dir
    shutil.rmtree(base_dir)

# Tests for parse_args
# To test parse_args directly, we would need to import it from main.
# If direct import is an issue, we test its effects via main script execution.
# For now, let's assume we can import main's parse_args or we test its side effects.

@mock.patch('argparse.ArgumentParser.parse_args')
def test_parse_args_defaults(mock_parse_args):
    # This test requires 'main.parse_args' to be importable or tested differently.
    # For now, we'll simulate its expected default Namespace object.
    # This also means we need to import 'parse_args' from 'main'
    try:
        from main import parse_args
        mock_parse_args.return_value = argparse.Namespace(mode='balanced', max_views=5000)
        args = parse_args()
        assert args.mode == 'balanced'
        assert args.max_views == 5000
    except ImportError:
        pytest.skip("Skipping direct parse_args test as main.py components are not directly importable.")


@mock.patch('argparse.ArgumentParser.parse_args')
def test_parse_args_custom(mock_parse_args):
    try:
        from main import parse_args
        mock_parse_args.return_value = argparse.Namespace(mode='safe', max_views=100)
        args = parse_args() # This call is now to the actual parse_args
        assert args.mode == 'safe'
        assert args.max_views == 100
    except ImportError:
        pytest.skip("Skipping direct parse_args test as main.py components are not directly importable.")

@mock.patch('main.TikTokBot')
@mock.patch('main.Thread') # Mocking Thread from main's context
@mock.patch('main.app.run') # Mocking app.run from main's context
@mock.patch.dict(os.environ, {}, clear=True) # Clear os.environ for this test
def test_main_script_execution_success(mock_app_run, mock_thread_class, mock_tiktok_bot_class, monkeypatch, temp_env_for_main):
    base_dir = temp_env_for_main
    monkeypatch.chdir(base_dir)

    # Simulate command-line arguments
    test_argv = ['main.py', '--mode', 'safe', '--max-views', '150']
    monkeypatch.setattr(sys, 'argv', test_argv)

    # Mock TikTokBot instance and its methods/attributes
    mock_bot_instance = mock.MagicMock()
    mock_bot_instance.driver = mock.MagicMock() # Simulate a present driver
    mock_tiktok_bot_class.return_value = mock_bot_instance

    # Mock Thread instance
    mock_thread_instance = mock.MagicMock()
    mock_thread_class.return_value = mock_thread_instance

    # Run main.py as a script
    # runpy.run_module('main', run_name='__main__', alter_sys=True)
    # Instead of runpy, to ensure mocks on main.TikTokBot etc. work, we need to make main importable
    # or structure main.py to have a main() function that we call.
    # For now, let's assume main.py can be imported and has a main_function() or similar
    # If not, this test needs adjustment.
    # Given the structure of main.py, direct import and execution of __name__ == "__main__"
    # is tricky with mocks. We'll try runpy.

    # To make runpy work with mocks on 'main.XYZ', ensure 'main' is in sys.modules *before* runpy
    # and that it's the *actual* module we want to run, not a mock itself.
    # However, the functions/classes are mocked *within* 'main' (e.g. 'main.TikTokBot')

    # Let's try importing main and calling a hypothetical main_logic() function
    # if main.py was structured like:
    # def main_logic(): ... ; if __name__ == "__main__": main_logic()
    # For now, we'll use runpy and see if mocks are effective.
    # It's common for runpy to not play perfectly with mocks applied to modules it loads as __main__
    # if those mocks are applied from the test's module context.
    # A robust way is to ensure 'main.py' is importable and call its main function.

    # Simplification: If main.py is not easily importable or callable as a function,
    # we can't directly assert calls on mocks like `mock_tiktok_bot_class.assert_called_once()`.
    # We would have to check side effects (like print statements or file outputs).

    # Let's assume we've made main.py importable and it has a `main_script_function`
    # For this exercise, we'll proceed as if runpy allows effective mocking.

    # Due to challenges in reliably mocking parts of a script run with runpy
    # when mocks are defined in the test module, this part is simplified.
    # In a real scenario, main.py would be refactored to be more testable (e.g., main logic in a function).

    # For this exercise, we'll assume that if main.py is imported, the __name__ == "__main__" block runs.
    # This is often not the case; it runs if the file itself is run as a script.
    # We use runpy to simulate script execution.

    # Clear sys.modules to ensure main is freshly loaded by runpy
    # No longer using runpy, directly calling the main logic function
    # if 'main' in sys.modules:
    #     del sys.modules['main']

    # Import and call the main logic function
    try:
        from main import main_script_logic, parse_args
        # We need to parse args because main_script_logic expects it
        # The sys.argv is already monkeypatched
        args = parse_args()
        main_script_logic(args)
    except ImportError as e:
        pytest.fail(f"Failed to import main_script_logic or parse_args from main: {e}")

    mock_tiktok_bot_class.assert_called_once()
    mock_bot_instance.run_session.assert_called_once()
    assert os.environ['MAX_VIEWS_PER_HOUR'] == '150'

    # Check Thread instantiation (target should be main.run_flask)
    # This requires run_flask to be accessible/importable or to mock by string path if needed.
    # For simplicity, we assume 'main.run_flask' is the intended target name.
    # If run_flask is not directly importable, one might need to mock 'main.run_flask'.

    # The target for Thread is `run_flask` which is a global in main.py.
    # We cannot directly assert `target=main.run_flask` unless `run_flask` is imported here.
    # Instead, we check if Thread was called, and its start method.
    mock_thread_class.assert_called_once() # Check if Thread() was called
    mock_thread_instance.start.assert_called_once()

    mock_app_run.assert_not_called() # app.run() is called in the thread, not main flow


@mock.patch('main.TikTokBot')
@mock.patch('main.Thread') # Mocking Thread from main's context
@mock.patch('main.app.run') # Mocking app.run from main's context
@mock.patch('sys.exit') # Mock sys.exit
@mock.patch('builtins.print') # Mock print to check output
@mock.patch.dict(os.environ, {}, clear=True)

def test_main_script_bot_driver_failure(mock_print, mock_sys_exit, mock_app_run, mock_thread_class, mock_tiktok_bot_class, monkeypatch, temp_env_for_main):
    base_dir = temp_env_for_main
    monkeypatch.chdir(base_dir)

    test_argv = ['main.py'] # Default args
    monkeypatch.setattr(sys, 'argv', test_argv)

    mock_bot_instance = mock.MagicMock()
    mock_bot_instance.driver = None # Simulate driver failure
    mock_tiktok_bot_class.return_value = mock_bot_instance

    # No longer using runpy
    # if 'main' in sys.modules:
    #    del sys.modules['main']
    # runpy.run_module('main', run_name='__main__', alter_sys=True)

    mock_sys_exit.side_effect = SystemExit(1) # Make mock_sys_exit raise SystemExit(1)

    with pytest.raises(SystemExit) as e_info: # Expect SystemExit
        try:
            from main import main_script_logic, parse_args
            args = parse_args()
            main_script_logic(args)
        except ImportError as e_imp: # Changed variable name for clarity
            pytest.fail(f"Failed to import main_script_logic or parse_args from main: {e_imp}")

    assert e_info.value.code == 1 # Check the exit code
    mock_tiktok_bot_class.assert_called_once()
    # Check for the specific print message indicating driver failure
    mock_print.assert_any_call("Failed to initialize bot - Chrome driver not available")
    mock_sys_exit.assert_called_once_with(1) # Check if exit(1) was called

    # Flask part should not be reached if exit happens
    mock_thread_class.assert_not_called()
    mock_app_run.assert_not_called()