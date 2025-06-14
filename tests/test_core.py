# Tests para los módulos principales en core/ del framework TTBT1
# Ejecutar con: pytest tests/test_core.py

import os
import json
import tempfile
from core.account_manager import AccountManager
from unittest import mock # Added
import builtins # Added for mocking print
from selenium.common.exceptions import NoSuchElementException # Added

from core.account_manager import AccountManager
from core.bot import TikTokBot
from core.bot_engine import BotEngine
from core.config_loader import load_config # Changed from ConfigLoader
from core.behavior import HumanBehaviorSimulator # Needed for spec in mock

# It's good practice to group tests in classes if using unittest.TestCase structure
# or if simply organizing related tests, even with pytest.
# For pytest, classes starting with Test are discovered.

class TestTikTokBot: # New class for TikTokBot tests
    # Moving existing test_bot_assign_proxy_and_fingerprint into this class
    def test_bot_assign_proxy_and_fingerprint(self): # Added self
        # This test relies on the __init__ taking _email and _account_details.
        # If __init__ changes, this test might need adjustment or be covered by new __init__ test.
        bot = TikTokBot("userx", {"pass": "xyz"})
        bot.assign_proxy("proxyX")
        bot.assign_fingerprint("fpY")
        assert bot.proxy == "proxyX"
        assert bot.fingerprint == "fpY"

    # --- Start of new TikTokBot tests ---

    @mock.patch('core.bot.HumanBehaviorSimulator')
    @mock.patch('core.bot.AccountManager')
    @mock.patch.object(TikTokBot, '_init_driver') # Mocking the method on the class
    def test_tiktokbot_init(self, mock_init_driver, mock_account_manager, mock_human_behavior_simulator):
        mock_driver_instance = mock.Mock()
        mock_init_driver.return_value = mock_driver_instance # _init_driver returns a driver

        bot = TikTokBot() # Call __init__

        mock_init_driver.assert_called_once()
        mock_account_manager.assert_called_once_with() # Assuming it's called with no args
        mock_human_behavior_simulator.assert_called_once_with(mock_driver_instance)
        assert bot.driver == mock_driver_instance # Corrected: self.assertEqual to assert
        assert bot.proxy is None # Corrected: self.assertIsNone to assert
        assert bot.fingerprint is None # Corrected: self.assertIsNone to assert

    @mock.patch('core.bot.webdriver.ChromeOptions')
    @mock.patch('core.bot.webdriver.Chrome')
    def test_tiktokbot_init_driver_calls(self, mock_chrome_driver, mock_chrome_options):
        # This test effectively tests _init_driver by calling __init__
        # but focuses on the webdriver.ChromeOptions and webdriver.Chrome calls.
        mock_options_instance = mock.Mock()
        mock_chrome_options.return_value = mock_options_instance

        # Need to ensure AccountManager and HumanBehaviorSimulator are also mocked if __init__ calls them
        with mock.patch('core.bot.AccountManager'), \
             mock.patch('core.bot.HumanBehaviorSimulator'):
            bot = TikTokBot() # This will call _init_driver

        expected_options_calls = [
            mock.call('--headless'),
            mock.call('--disable-gpu'),
            mock.call('--no-sandbox'),
            mock.call('user-agent=Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36')
        ]
        mock_options_instance.add_argument.assert_has_calls(expected_options_calls, any_order=False)
        mock_chrome_driver.assert_called_once_with(options=mock_options_instance)


    def test_tiktokbot_authenticate_success(self):
        # Setup bot with mocked dependencies
        # Mock _init_driver directly on the class for this instance
        with mock.patch.object(TikTokBot, '_init_driver', return_value=mock.MagicMock()) as mock_init_driver_method:
            # Mock other dependencies that are instantiated in __init__
            with mock.patch('core.bot.AccountManager') as MockAccountManager, \
                 mock.patch('core.bot.HumanBehaviorSimulator') as MockBehaviorSimulator:

                mock_am_instance = mock.MagicMock(spec=AccountManager)
                MockAccountManager.return_value = mock_am_instance

                mock_bhs_instance = mock.MagicMock(spec=HumanBehaviorSimulator)
                MockBehaviorSimulator.return_value = mock_bhs_instance

                bot = TikTokBot() # __init__ uses the mocks

        mock_driver = bot.driver # This is the MagicMock from _init_driver

        # Ensure account_manager and behavior are the instances we expect (the mocks)
        bot.account_manager = mock_am_instance
        bot.behavior = mock_bhs_instance

        # Configure mocks for success path
        mock_account = {"email": "test@example.com", "password": "password123"}
        bot.account_manager.get_next_account.return_value = mock_account

        mock_email_field = mock.Mock()
        mock_pass_field = mock.Mock()
        mock_submit_btn = mock.Mock()

        # Configure find_element to return different mocks based on name/xpath
        def find_element_side_effect(by, value):
            if value == "username": return mock_email_field
            if value == "password": return mock_pass_field
            if value == '//button[@type="submit"]': return mock_submit_btn
            raise NoSuchElementException(f"No mock for {value}")

        mock_driver.find_element.side_effect = find_element_side_effect

        # Call the method
        result = bot._authenticate()

        # Assertions
        assert result is True # Corrected: self.assertTrue to assert
        bot.account_manager.get_next_account.assert_called_once()
        mock_driver.get.assert_called_once_with("https://www.tiktok.com/login")

        # Check calls to behavior simulator
        bot.behavior.random_delay.assert_called_once_with(3, 5)
        bot.behavior.human_type.assert_any_call(mock_email_field, "test@example.com")
        bot.behavior.human_type.assert_any_call(mock_pass_field, "password123")
        bot.behavior.human_click.assert_called_once_with(mock_submit_btn)

        # Check find_element calls (By value is implicitly tested by side_effect keys)
        assert mock_driver.find_element.call_count == 3 # Corrected: self.assertEqual to assert

    @mock.patch('builtins.print') # To capture print output
    def test_tiktokbot_authenticate_failure_no_account(self, mock_print):
        with mock.patch.object(TikTokBot, '_init_driver', return_value=mock.MagicMock()):
            # Mock dependencies instantiated in __init__
            with mock.patch('core.bot.AccountManager') as MockAccountManager, \
                 mock.patch('core.bot.HumanBehaviorSimulator'): # Mock BHS as well

                mock_am_instance = mock.MagicMock(spec=AccountManager)
                MockAccountManager.return_value = mock_am_instance
                bot = TikTokBot()

        bot.account_manager = mock_am_instance # Ensure bot uses our mock instance
        bot.account_manager.get_next_account.return_value = None # Simulate no account available

        result = bot._authenticate()

        assert not result
        bot.account_manager.get_next_account.assert_called_once()
        mock_print.assert_called_with("No se encontró ninguna cuenta válida en la base de datos.")

    @mock.patch('builtins.print')
    def test_tiktokbot_authenticate_failure_selenium_exception(self, mock_print):
        with mock.patch.object(TikTokBot, '_init_driver', return_value=mock.MagicMock()) as mock_init_driver:
            # Mock dependencies instantiated in __init__
            with mock.patch('core.bot.AccountManager') as MockAccountManager, \
                 mock.patch('core.bot.HumanBehaviorSimulator') as MockBehaviorSimulator:

                mock_am_instance = mock.MagicMock(spec=AccountManager)
                MockAccountManager.return_value = mock_am_instance

                mock_bhs_instance = mock.MagicMock(spec=HumanBehaviorSimulator)
                MockBehaviorSimulator.return_value = mock_bhs_instance

                bot = TikTokBot()

        mock_driver = bot.driver
        bot.account_manager = mock_am_instance # Ensure bot uses our mock instance
        bot.behavior = mock_bhs_instance # Ensure bot uses our mock instance


        mock_account = {"email": "test@example.com", "password": "password123"}
        bot.account_manager.get_next_account.return_value = mock_account

        # Simulate an exception during a Selenium operation (e.g., finding an element)
        # Let's assume driver.get works, but find_element fails on the first try
        mock_driver.find_element.side_effect = NoSuchElementException("Mocked element not found")

        result = bot._authenticate()

        assert not result
        mock_driver.get.assert_called_once_with("https://www.tiktok.com/login")
        # find_element was called, and it raised an exception
        mock_driver.find_element.assert_called()
        # Check if the specific error message was printed
        error_message_found = False
        for call_args in mock_print.call_args_list:
            if "Error de autenticación:" in call_args[0][0]:
                error_message_found = True
                break
        assert error_message_found, "Expected authentication error message not printed."

    @mock.patch.object(TikTokBot, '_perform_organic_actions')
    @mock.patch.object(TikTokBot, '_authenticate')
    def test_tiktokbot_run_session_auth_success(self, mock_authenticate, mock_perform_organic_actions):
        with mock.patch.object(TikTokBot, '_init_driver', return_value=mock.MagicMock()):
            # Mock dependencies instantiated in __init__ to avoid their side effects
            with mock.patch('core.bot.AccountManager'), \
                 mock.patch('core.bot.HumanBehaviorSimulator'):
                bot = TikTokBot()

        mock_authenticate.return_value = True # Simulate successful authentication

        bot.run_session()

        mock_authenticate.assert_called_once()
        mock_perform_organic_actions.assert_called_once()

    @mock.patch.object(TikTokBot, '_perform_organic_actions')
    @mock.patch.object(TikTokBot, '_authenticate')
    def test_tiktokbot_run_session_auth_failure(self, mock_authenticate, mock_perform_organic_actions):
        with mock.patch.object(TikTokBot, '_init_driver', return_value=mock.MagicMock()):
            # Mock dependencies instantiated in __init__
            with mock.patch('core.bot.AccountManager'), \
                 mock.patch('core.bot.HumanBehaviorSimulator'):
                bot = TikTokBot()

        mock_authenticate.return_value = False # Simulate failed authentication

        bot.run_session()

        mock_authenticate.assert_called_once()
        mock_perform_organic_actions.assert_not_called()

    @mock.patch('core.bot.time.sleep') # Mock time.sleep
    @mock.patch('core.bot.random.random') # Mock random.random for like probability
    @mock.patch('core.bot.os.getenv') # Mock os.getenv for MAX_VIEWS_PER_HOUR
    def test_tiktokbot_perform_organic_actions(self, mock_getenv, mock_random, mock_time_sleep):
        with mock.patch.object(TikTokBot, '_init_driver', return_value=mock.MagicMock()):
            # Mock dependencies instantiated in __init__
            with mock.patch('core.bot.AccountManager'), \
                 mock.patch('core.bot.HumanBehaviorSimulator') as MockBehaviorSimulator:
                mock_bhs_instance = mock.MagicMock(spec=HumanBehaviorSimulator)
                MockBehaviorSimulator.return_value = mock_bhs_instance
                bot = TikTokBot()

        # Ensure behavior is the mock instance for this test
        bot.behavior = mock_bhs_instance

        # Setup mock return values
        mock_getenv.return_value = "3" # Simulate 3 views
        mock_random.return_value = 0.5 # Simulate a 50% chance of liking (will like if < 0.65)

        bot._perform_organic_actions()

        mock_getenv.assert_called_once_with("MAX_VIEWS_PER_HOUR", "50")
        assert bot.behavior.watch_video.call_count == 3
        assert bot.behavior.like_video.call_count == 3 # Since 0.5 < 0.65
        assert bot.behavior.random_scroll.call_count == 3
        assert mock_time_sleep.call_count == 3

    @mock.patch('core.bot.time.sleep')
    @mock.patch('core.bot.random.random')
    @mock.patch('core.bot.os.getenv')
    def test_tiktokbot_perform_organic_actions_no_like(self, mock_getenv, mock_random, mock_time_sleep):
        with mock.patch.object(TikTokBot, '_init_driver', return_value=mock.MagicMock()):
            # Mock dependencies instantiated in __init__
            with mock.patch('core.bot.AccountManager'), \
                 mock.patch('core.bot.HumanBehaviorSimulator') as MockBehaviorSimulator:
                mock_bhs_instance = mock.MagicMock(spec=HumanBehaviorSimulator)
                MockBehaviorSimulator.return_value = mock_bhs_instance
                bot = TikTokBot()

        bot.behavior = mock_bhs_instance

        mock_getenv.return_value = "2" # Simulate 2 views
        mock_random.return_value = 0.7 # Simulate a 70% chance (will NOT like if < 0.65)

        bot._perform_organic_actions()

        mock_getenv.assert_called_once_with("MAX_VIEWS_PER_HOUR", "50")
        assert bot.behavior.watch_video.call_count == 2
        assert bot.behavior.like_video.call_count == 0 # Should not like
        assert bot.behavior.random_scroll.call_count == 2
        assert mock_time_sleep.call_count == 2

    # --- End of new TikTokBot tests ---

# Standalone tests for AccountManager - to be moved or kept if style allows
def test_account_manager_load_accounts_standalone(): # Renamed to avoid conflict if class below is used by pytest
    data = {"usera": {"pass": "123"}, "userb": {"pass": "456"}}
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as f:
        json.dump(data, f)
        f.seek(0)
        manager = AccountManager(f.name)
        assert manager.accounts == data
    os.remove(f.name)

def test_account_manager_file_not_found():
    manager = AccountManager("noexiste.json")
    assert manager.accounts == {}

class TestAccountManagerMethods: # Using pytest-style class

    def test_init_malformed_json(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as f:
            f.write("{not_json: this_will_fail,}")
            f.seek(0)
            filepath = f.name

        manager = AccountManager(filepath)
        assert manager.accounts == {} # Should default to empty on parse error
        os.remove(filepath)

    def test_add_account_new_and_update(self):
        manager = AccountManager() # No filepath, starts empty
        manager.add_account("test@example.com", "pass1")
        assert manager.accounts == {"test@example.com": {"password": "pass1"}}

        manager.add_account("another@example.com", "pass2")
        assert manager.accounts == {
            "test@example.com": {"password": "pass1"},
            "another@example.com": {"password": "pass2"}
        }

        # Update existing
        manager.add_account("test@example.com", "newpass")
        assert manager.accounts == {
            "test@example.com": {"password": "newpass"},
            "another@example.com": {"password": "pass2"}
        }

    def test_get_next_account_empty(self):
        manager = AccountManager()
        assert manager.get_next_account() is None

    def test_get_next_account_single(self):
        manager = AccountManager()
        manager.add_account("test@example.com", "pass1")
        expected = {"email": "test@example.com", "password": "pass1"}
        assert manager.get_next_account() == expected

    def test_get_next_account_multiple_sorted_order(self):
        manager = AccountManager()
        manager.add_account("b@example.com", "passB")
        manager.add_account("a@example.com", "passA")
        manager.add_account("c@example.com", "passC")

        # get_next_account sorts keys and picks the first one
        expected = {"email": "a@example.com", "password": "passA"}
        assert manager.get_next_account() == expected

        # Verify it's non-destructive and repeatable for current implementation
        assert manager.get_next_account() == expected

    @mock.patch('core.account_manager.os.path.exists') # Corrected patch target
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_init_io_error_on_open(self, mock_open, mock_os_path_exists):
        mock_os_path_exists.return_value = True # File exists
        mock_open.side_effect = IOError("Simulated file read error") # open() itself raises IOError

        manager = AccountManager('dummy_path.json')

        mock_os_path_exists.assert_called_once_with('dummy_path.json')
        mock_open.assert_called_once_with('dummy_path.json', 'r', encoding='utf-8')
        assert manager.accounts == {} # Should default to empty on IOError

    def test_get_next_account_accounts_is_not_dict_but_not_empty(self):
        # This test is to cover the final 'return None' in get_next_account,
        # which occurs if self.accounts is not a dict but also not empty
        # (an unlikely state with current methods, but tests completeness).
        with mock.patch('core.account_manager.os.path.exists', return_value=False):
             manager = AccountManager() # Initializes self.accounts as {}

        # Manually set accounts to an unexpected non-empty, non-dict type
        manager.accounts = ["not_a_dict_account_list_item"]

        result = manager.get_next_account()
        assert result is None

# Keep other tests as standalone functions if they don't fit TestTikTokBot or other classes
# Or create other test classes for them (e.g., TestAccountManager, TestBotEngine)

def test_bot_engine_initialization(monkeypatch):
    accounts = {"bot1": {"pass": "a"}, "bot2": {"pass": "b"}}
    # Gestores dummy que siempre devuelven el mismo valor
    class DummyProxyManager:
        def get_random_active_proxy(self): return "proxyZ"
    class DummyFingerprintManager:
        def get_fingerprint(self): return "fpW"
    engine = BotEngine(accounts, DummyProxyManager(), DummyFingerprintManager())
    engine.initialize_bots()
    assert len(engine.bots) == 2
    for bot in engine.bots:
        assert bot.proxy == "proxyZ"
        assert bot.fingerprint == "fpW"

def test_config_loader_json_and_yaml():
    data = {"hello": "world"}
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as jf:
        json.dump(data, jf)
        jf.seek(0)
        loaded = load_config(jf.name) # Changed from ConfigLoader.load
        assert loaded == data
    os.remove(jf.name)
    try:
        import yaml
        with tempfile.NamedTemporaryFile("w+", suffix=".yml", delete=False) as yf:
            yaml.safe_dump(data, yf)
            yf.seek(0)
            loaded = load_config(yf.name) # Changed from ConfigLoader.load
            assert loaded == data
        os.remove(yf.name)
    except ImportError:
        pass

# New tests for load_config FileNotFoundError
@mock.patch('builtins.open') # Patch open globally for the test
def test_load_config_json_file_not_found(mock_open_func):
    mock_open_func.side_effect = FileNotFoundError("Simulated File Not Found")
    result = load_config("dummy.json")
    assert result == {}
    mock_open_func.assert_called_once_with("dummy.json", "r", encoding="utf-8")

@mock.patch('builtins.open') # Patch open globally for the test
def test_load_config_yaml_file_not_found(mock_open_func):
    mock_open_func.side_effect = FileNotFoundError("Simulated File Not Found")
    result = load_config("dummy.yaml")
    assert result == {}
    mock_open_func.assert_called_once_with("dummy.yaml", "r", encoding="utf-8")

def test_load_config_unknown_extension():
    # No need to mock open, as it shouldn't be called if extension is not matched.
    result = load_config("somefile.txt")
    assert result == {}

# --- New tests for BotEngine ---

@mock.patch('builtins.print')
@mock.patch('core.bot_engine.TikTokBot') # To prevent actual TikTokBot instantiation
def test_bot_engine_initialize_bots_accounts_not_dict(mock_tiktok_bot, mock_print):
    # Dummy managers
    mock_proxy_manager = mock.Mock()
    mock_fingerprint_manager = mock.Mock()

    accounts_list = ["not_a_dict"] # Pass a list instead of a dict
    engine = BotEngine(accounts_list, mock_proxy_manager, mock_fingerprint_manager)
    engine.initialize_bots()

    assert engine.bots == [] # Bots list should remain empty
    mock_print.assert_called_with("Accounts data is not in the expected dictionary format.")
    mock_tiktok_bot.assert_not_called() # TikTokBot should not have been instantiated

@mock.patch('core.bot_engine.TikTokBot')
def test_bot_engine_initialize_bots_no_proxy(mock_tiktok_bot_class):
    mock_bot_instance = mock.MagicMock(spec=TikTokBot)
    mock_tiktok_bot_class.return_value = mock_bot_instance

    accounts = {"bot1": {"pass": "a"}}
    mock_proxy_manager = mock.Mock()
    mock_proxy_manager.get_random_active_proxy.return_value = None # Simulate no proxy
    mock_fingerprint_manager = mock.Mock()
    mock_fingerprint_manager.get_fingerprint.return_value = "fpTest"

    engine = BotEngine(accounts, mock_proxy_manager, mock_fingerprint_manager)
    engine.initialize_bots()

    assert len(engine.bots) == 1
    mock_tiktok_bot_class.assert_called_once_with(_email="bot1", _account_details={"pass": "a"})
    mock_bot_instance.assign_proxy.assert_not_called() # Proxy assignment should not be called
    mock_bot_instance.assign_fingerprint.assert_called_once_with("fpTest")

@mock.patch('core.bot_engine.TikTokBot')
def test_bot_engine_initialize_bots_no_fingerprint(mock_tiktok_bot_class):
    mock_bot_instance = mock.MagicMock(spec=TikTokBot)
    mock_tiktok_bot_class.return_value = mock_bot_instance

    accounts = {"bot1": {"pass": "a"}}
    mock_proxy_manager = mock.Mock()
    mock_proxy_manager.get_random_active_proxy.return_value = "proxyTest"
    mock_fingerprint_manager = mock.Mock()
    mock_fingerprint_manager.get_fingerprint.return_value = None # Simulate no fingerprint

    engine = BotEngine(accounts, mock_proxy_manager, mock_fingerprint_manager)
    engine.initialize_bots()

    assert len(engine.bots) == 1
    mock_tiktok_bot_class.assert_called_once_with(_email="bot1", _account_details={"pass": "a"})
    mock_bot_instance.assign_proxy.assert_called_once_with("proxyTest")
    mock_bot_instance.assign_fingerprint.assert_not_called() # Fingerprint assignment should not be called

@mock.patch('core.bot_engine.TikTokBot') # Mock TikTokBot to control its instances
def test_bot_engine_run_method_calls_run_session(mock_tiktok_bot_class):
    # Create mock instances for TikTokBot that will be "created" by initialize_bots
    mock_bot_instance1 = mock.MagicMock(spec=TikTokBot)
    mock_bot_instance2 = mock.MagicMock(spec=TikTokBot)

    # Configure the mock TikTokBot class to return these instances sequentially
    mock_tiktok_bot_class.side_effect = [mock_bot_instance1, mock_bot_instance2]

    accounts = {"bot1": {"pass": "a"}, "bot2": {"pass": "b"}}
    mock_proxy_manager = mock.Mock()
    mock_proxy_manager.get_random_active_proxy.return_value = "proxyTest"
    mock_fingerprint_manager = mock.Mock()
    mock_fingerprint_manager.get_fingerprint.return_value = "fpTest"

    engine = BotEngine(accounts, mock_proxy_manager, mock_fingerprint_manager)

    # Call run, which should call initialize_bots, then run_session on each bot
    engine.run()

    assert mock_tiktok_bot_class.call_count == 2 # Two bots initialized
    assert len(engine.bots) == 2

    mock_bot_instance1.run_session.assert_called_once()
    mock_bot_instance2.run_session.assert_called_once()

@mock.patch('builtins.print')
@mock.patch('core.bot_engine.TikTokBot')
def test_bot_engine_run_method_initializes_if_bots_empty(mock_tiktok_bot_class, mock_print):
    mock_bot_instance = mock.MagicMock(spec=TikTokBot)
    mock_tiktok_bot_class.return_value = mock_bot_instance

    accounts = {"bot1": {"pass": "a"}}
    mock_proxy_manager = mock.Mock()
    mock_proxy_manager.get_random_active_proxy.return_value = "proxyTest"
    mock_fingerprint_manager = mock.Mock()
    mock_fingerprint_manager.get_fingerprint.return_value = "fpTest"

    engine = BotEngine(accounts, mock_proxy_manager, mock_fingerprint_manager)
    # Do not call engine.initialize_bots() here explicitly

    engine.run() # run() should call initialize_bots()

    assert len(engine.bots) == 1
    mock_tiktok_bot_class.assert_called_once() # Should be called by initialize_bots within run
    engine.bots[0].run_session.assert_called_once()

@mock.patch('builtins.print')
@mock.patch('core.bot_engine.TikTokBot')
def test_bot_engine_run_method_handles_initialize_bots_failure(mock_tiktok_bot_class, mock_print):
    # Dummy managers
    mock_proxy_manager = mock.Mock()
    mock_fingerprint_manager = mock.Mock()

    accounts_list = ["not_a_dict"] # Pass a list instead of a dict
    engine = BotEngine(accounts_list, mock_proxy_manager, mock_fingerprint_manager)

    engine.run() # This will call initialize_bots, which will print and return

    assert engine.bots == [] # Bots list should remain empty
    mock_print.assert_any_call("Accounts data is not in the expected dictionary format.")
    # Ensure run_session is not called on any bot since self.bots is empty
    # (This is implicitly tested by not having any bots to iterate over)