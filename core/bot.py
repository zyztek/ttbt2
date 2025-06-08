"""
This module defines bot-related classes for the TTBT1 framework.

It includes:
- A generic base `Bot` class providing a foundational structure for bots.
- The specialized `TikTokBot` class, which encapsulates the core logic for
  interacting with the TikTok website, including WebDriver management,
  authentication, and performing 'organic' user actions.
"""
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from core.account_manager import CoreAccountManager
from core.evasion import HumanBehaviorSimulator
from core.logger import get_logger

# --- Base Bot Class ---
class Bot:
    """
    A generic base class for bots in the TTBT1 framework.

    This class provides a basic structure for bots, including initialization
    of common attributes like username, account data, proxy, and fingerprint.
    Subclasses are expected to implement their own specific `run` logic.
    This class is not intended for direct Selenium WebDriver interaction by default.
    """
    def __init__(self, username, account_data):
        """
        Initializes the base Bot.

        Args:
            username (str): The username associated with this bot instance.
            account_data (dict): A dictionary containing account-specific data
                                 (e.g., password, settings).
        """
        self.username = username
        self.account_data = account_data
        self.proxy = None         # To be assigned by bot runner or specific logic
        self.fingerprint = None   # To be assigned by bot runner or specific logic
        # Note: Consider adding a logger here if general Bot instances need logging
        # self.bot_logger = get_logger(f"Bot.{self.username}") # Renamed to avoid clash

    def assign_proxy(self, proxy_string):
        """Assigns a proxy to the bot."""
        self.proxy = proxy_string
        # if hasattr(self, 'bot_logger'): self.bot_logger.info(f"Assigned proxy: {self.proxy}")

    def assign_fingerprint(self, fingerprint_string):
        """Assigns a fingerprint to the bot."""
        self.fingerprint = fingerprint_string
        # if hasattr(self, 'bot_logger'): self.bot_logger.info(f"Assigned fingerprint: {self.fingerprint}")

    def run(self):
        """
        The main execution method for the bot.
        Subclasses must implement this method to define their specific behavior.
        """
        raise NotImplementedError("Subclasses must implement the 'run' method.")

# --- TikTok Specific Bot ---

# Initialize a logger for the TikTokBot module/class
# This logger is specific to TikTokBot operations.
logger = get_logger("TikTokBot")

class TikTokBot:
    """
    The main class for the TikTok Bot, specialized for TikTok interactions.
    This class is responsible for:
    - Initializing and configuring the Selenium WebDriver for TikTok.
    - Managing account credentials via an AccountManager.
    - Handling the authentication process on TikTok.
    - Performing a series of 'organic' actions like watching videos,
      liking content, and scrolling, simulated via HumanBehaviorSimulator.

    Attributes:
        driver: The Selenium WebDriver instance used to interact with the browser.
        mode (str): The operational mode of the bot (e.g., 'safe', 'balanced').
        account_manager (CoreAccountManager): Manages retrieval of account credentials.
        behavior (HumanBehaviorSimulator): Simulates human-like interactions.
        LOGIN_URL (str): The URL for the TikTok login page.
        USERNAME_FIELD_BY: Selenium locator strategy for the username field.
        USERNAME_FIELD_VALUE (str): Selenium locator value for the username field.
        PASSWORD_FIELD_BY: Selenium locator strategy for the password field.
        PASSWORD_FIELD_VALUE (str): Selenium locator value for the password field.
        SUBMIT_BUTTON_BY: Selenium locator strategy for the submit button.
        SUBMIT_BUTTON_VALUE (str): Selenium locator value for the submit button.
        shared_status (dict, optional): A dictionary for sharing status with other threads.
        status_lock (threading.Lock, optional): A lock for synchronizing access to shared_status.
    """
    def __init__(self, mode='balanced', shared_status=None, status_lock=None):
        """
        Initializes the TikTokBot.

        Args:
            mode (str, optional): The operational mode for the bot. Defaults to 'balanced'.
            shared_status (dict, optional): Dictionary for inter-thread status sharing.
            status_lock (threading.Lock, optional): Lock for synchronizing shared_status access.
        """
        # self.logger = get_logger(f"TikTokBot.{mode}") # Alternative: instance-specific logger with mode
        logger.info(f"Initializing TikTokBot with mode: {mode}")

        self.shared_status = shared_status
        self.status_lock = status_lock
        self.session_actions_count = 0 # Initialize session action counter

        self._update_shared_status({"mode": mode, "status": "initializing_webdriver"})
        self.driver = self._init_driver()
        self.mode = mode
        self.account_manager = CoreAccountManager() # Manages TikTok account credentials

        if self.driver:
            self.behavior = HumanBehaviorSimulator(self.driver, mode=self.mode)
            self._update_shared_status({"status": "initialized_ready"})
        else:
            logger.error("HumanBehaviorSimulator not initialized due to WebDriver failure.")
            self.behavior = None
            self._update_shared_status({
                "status": "error_webdriver_init",
                "last_error": "WebDriver failed to initialize during bot __init__."
            })

        # Centralized Selectors for the TikTok Login Page
        # These help in maintaining and updating element locators easily.
        self.LOGIN_URL = "https://www.tiktok.com/login"
        self.USERNAME_FIELD_BY = By.NAME
        self.USERNAME_FIELD_VALUE = "username" # Standard name attribute for username input
        self.PASSWORD_FIELD_BY = By.NAME
        self.PASSWORD_FIELD_VALUE = "password" # Standard name attribute for password input
        self.SUBMIT_BUTTON_BY = By.XPATH
        # This XPath targets a button element with type="submit".
        # It's a common pattern but might need adjustment if TikTok's UI changes.
        self.SUBMIT_BUTTON_VALUE = '//button[@type="submit"]'

    def _init_driver(self):
        """
        Configures and initializes the Selenium Chrome WebDriver.

        Sets Chrome options for headless browsing, disabling GPU, running in a sandbox,
        and a specific mobile user-agent to mimic a mobile device.

        Returns:
            webdriver.Chrome or None: The initialized WebDriver instance, or None if
                                      initialization fails.
        """
        logger.debug("Initializing WebDriver.")
        options = webdriver.ChromeOptions()
        # Common options for running in automated environments / headless
        options.add_argument("--headless") # Run Chrome in headless mode (no GUI).
        options.add_argument("--disable-gpu") # Disable GPU hardware acceleration. Often needed for headless.
        options.add_argument("--no-sandbox") # Bypass OS security model. Useful in Docker/CI environments.
        # Mimic a mobile user agent. TikTok's mobile interface might be simpler or different.
        options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36")

        try:
            driver = webdriver.Chrome(options=options)
            logger.info("WebDriver initialized successfully.")
            return driver
        except WebDriverException as e:
            # Log detailed error if WebDriver fails to initialize (e.g., chromedriver not in PATH)
            logger.error(f"Failed to initialize WebDriver: {e}")
            return None

    def _authenticate(self):
        """
        Handles the authentication process for a TikTok account.

        Retrieves account credentials, navigates to the login page,
        fills in the username and password, and submits the form.
        Uses HumanBehaviorSimulator for typing and clicking to appear more human-like.

        Returns:
            bool: True if authentication is believed to be successful, False otherwise.
                  Note: Success is currently inferred by lack of exceptions during the process.
                  A more robust check would verify a post-login state.
        """
        account = self.account_manager.get_next_account()
        if not account or not account.get("email") or not account.get("password"):
            # Log a warning if no valid account details are found.
            logger.warning("Authentication skipped: No valid account credentials found in AccountManager.")
            self._update_shared_status({
                "status": "error_no_account",
                "current_user": None,
                "last_error": "No valid account credentials found."
            })
            return False

        logger.info(f"Attempting to authenticate with account: {account.get('email')}")
        self._update_shared_status({
            "status": "authenticating",
            "current_user": account.get('email'),
            "last_error": None
        })

        if not self.driver or not self.behavior:
            logger.error("Authentication cannot proceed: WebDriver or HumanBehaviorSimulator not initialized.")
            self._update_shared_status({
                "status": "error_internal_bot_setup",
                "last_error": "WebDriver or BehaviorSimulator not ready for auth."
            })
            return False

        try:
            logger.debug(f"Navigating to login page: {self.LOGIN_URL}")
            self.driver.get(self.LOGIN_URL)
            self.behavior.random_delay(3, 5) # Wait for page elements to potentially load

            # Fill in username/email
            logger.debug(f"Locating username field using: {self.USERNAME_FIELD_BY}, {self.USERNAME_FIELD_VALUE}")
            email_field = self.driver.find_element(self.USERNAME_FIELD_BY, self.USERNAME_FIELD_VALUE)
            self.behavior.human_type(email_field, account['email'])
            logger.debug("Username field filled.")

            # Fill in password
            logger.debug(f"Locating password field using: {self.PASSWORD_FIELD_BY}, {self.PASSWORD_FIELD_VALUE}")
            pass_field = self.driver.find_element(self.PASSWORD_FIELD_BY, self.PASSWORD_FIELD_VALUE)
            self.behavior.human_type(pass_field, account['password'])
            logger.debug("Password field filled.")

            # Click submit button
            logger.debug(f"Locating submit button using: {self.SUBMIT_BUTTON_BY}, {self.SUBMIT_BUTTON_VALUE}")
            submit_btn = self.driver.find_element(self.SUBMIT_BUTTON_BY, self.SUBMIT_BUTTON_VALUE)
            self.behavior.human_click(submit_btn)
            logger.info("Login form submitted.")

            # It's crucial to add a post-login check here.
            # For example, wait for a specific element on the home page or check if the URL changed.
            # current_url = self.driver.current_url
            # if "login" not in current_url:
            # logger.info("Authentication seems successful (URL changed).")
            # else:
            # logger.warning("Authentication may have failed (still on login page or login-related URL).")
            # return False
            # For now, we assume success if no exceptions occur.
            logger.info("Authentication process completed.")
            self._update_shared_status({"status": "authenticated"})
            return True
        except (NoSuchElementException, TimeoutException) as specific_selenium_error:
            err_msg = f"Selenium error during auth: {specific_selenium_error}"
            logger.error(f"Authentication failed: {err_msg}")
            self._update_shared_status({"status": "error_auth_failed", "last_error": err_msg})
            return False
        except WebDriverException as wd_error:
            err_msg = f"WebDriver error during auth: {wd_error}"
            logger.error(f"Authentication failed: {err_msg}")
            self._update_shared_status({"status": "error_auth_failed", "last_error": err_msg})
            return False
        except Exception as e:
            err_msg = f"Unexpected error during auth: {e}"
            logger.exception(err_msg)
            self._update_shared_status({"status": "error_auth_failed", "last_error": err_msg})
            return False

    def _update_shared_status(self, updates_dict):
        """Helper method to update the shared status dictionary with thread safety."""
        if self.shared_status is not None and self.status_lock is not None:
            with self.status_lock:
                for key, value in updates_dict.items():
                    self.shared_status[key] = value
            logger.trace(f"Shared status updated with: {updates_dict}. Current status: {self.shared_status.get('status')}")
        else:
            logger.trace("Shared status or lock not provided; skipping status update.")


    def run_session(self):
        """
        Orchestrates a single bot session.

        This involves attempting to authenticate and, if successful, performing
        a series of organic actions. Updates shared status throughout.
        """
        logger.info("Starting new bot session.")
        self.session_actions_count = 0 # Reset session action counter
        self._update_shared_status({
            "actions_this_session": self.session_actions_count,
            "status": "session_starting" # Initial status for the session run
        })

        if self.driver is None:
            logger.error("Cannot run session: WebDriver is not initialized.")
            # This state should have been set in __init__ already if driver failed there
            # self._update_shared_status({"status": "error_webdriver_not_ready", "last_error": "WebDriver missing at session start."})
            return

        if self._authenticate(): # This method now updates status internally
            logger.info("Authentication successful. Proceeding to perform organic actions.")
            self._update_shared_status({"status": "running_actions"}) # Status after successful auth
            self._perform_organic_actions()
            self._update_shared_status({"status": "session_complete"}) # If actions loop completes
        else:
            logger.warning("Authentication failed. Organic actions will not be performed this session.")
            # _authenticate method should have set the appropriate error status.
        logger.info("Bot session finished.")


    def _perform_organic_actions(self):
        """
        Performs a loop of simulated organic user actions on TikTok.

        Actions include watching videos, liking videos (with a certain probability),
        and scrolling. The number of actions (simulated views) is controlled by
        the `MAX_VIEWS_PER_HOUR` environment variable.
        """
        if not self.behavior:
            logger.error("Cannot perform organic actions: HumanBehaviorSimulator is not initialized.")
            return

        logger.info("Starting to perform organic actions.")
        # Get max views from environment variable, default to 50 if not set or invalid.
        try:
            max_views = int(os.getenv("MAX_VIEWS_PER_HOUR", "50"))
        except ValueError:
            logger.warning("Invalid MAX_VIEWS_PER_HOUR value, defaulting to 50.")
            max_views = 50

        logger.info(f"Session configured to perform up to {max_views} view actions.")

        for i in range(max_views):
            logger.debug(f"Organic action cycle {i+1} of {max_views}.")

            self.behavior.watch_video()

            like_probability = 0.65
            if random.random() < like_probability:
                logger.debug(f"Attempting to like video (probability: {like_probability*100}%).")
                self.behavior.like_video()
            else:
                logger.debug(f"Skipping like for this video (probability: {like_probability*100}%).")

            self.behavior.random_scroll()

            # Update actions count for this session
            self.session_actions_count += 1
            self._update_shared_status({"actions_this_session": self.session_actions_count})

            base_sleep_time = random.uniform(8, 15)
            logger.debug(f"Pausing for {base_sleep_time:.2f} seconds between action cycles.")
            time.sleep(base_sleep_time)

            # TODO: Consider if bot needs to check shared_status for a "stop_requested" flag from dashboard

        logger.info(f"Completed {max_views} organic action cycles for the session.")