"""
This module defines the TikTokBot class, which encapsulates the core logic for
interacting with the TikTok website. This includes managing the WebDriver,
handling user authentication, and performing various 'organic' user actions.
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

# Initialize a logger for this module
logger = get_logger("TikTokBot")

class TikTokBot:
    """
    The main class for the TikTok Bot.

    This class is responsible for:
    - Initializing and configuring the Selenium WebDriver.
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
    """
    def __init__(self, mode='balanced'):
        """
        Initializes the TikTokBot.

        Args:
            mode (str, optional): The operational mode for the bot.
                                  Defaults to 'balanced'. This mode is passed to
                                  the HumanBehaviorSimulator.
        """
        # self.logger = get_logger(f"TikTokBot.{mode}") # Alternative: instance-specific logger with mode
        logger.info(f"Initializing TikTokBot with mode: {mode}")
        self.driver = self._init_driver()
        self.mode = mode
        self.account_manager = CoreAccountManager() # Manages TikTok account credentials

        # Initialize HumanBehaviorSimulator if driver initialization was successful
        if self.driver:
            self.behavior = HumanBehaviorSimulator(self.driver, mode=self.mode)
        else:
            # This case should ideally be handled more gracefully,
            # perhaps by raising an exception if driver is critical.
            logger.error("HumanBehaviorSimulator not initialized due to WebDriver failure.")
            self.behavior = None

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
            return False

        logger.info(f"Attempting to authenticate with account: {account.get('email')}")
        if not self.driver or not self.behavior:
            logger.error("Authentication cannot proceed: WebDriver or HumanBehaviorSimulator not initialized.")
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
            logger.info("Authentication process completed (assumed successful if no errors).")
            return True
        except (NoSuchElementException, TimeoutException) as specific_selenium_error:
            logger.error(f"Authentication failed (Selenium error): Element not found or operation timed out. Details: {specific_selenium_error}")
            return False
        except WebDriverException as wd_error:
            # This can happen if the browser crashes or WebDriver loses connection.
            logger.error(f"Authentication failed (WebDriver error): {wd_error}")
            return False
        except Exception as e:
            # Catch-all for any other unexpected errors during authentication.
            logger.exception("An unexpected error occurred during the authentication process:")
            return False

    def run_session(self):
        """
        Orchestrates a single bot session.

        This involves attempting to authenticate and, if successful, performing
        a series of organic actions.
        """
        logger.info("Starting new bot session.")
        if self.driver is None:
            logger.error("Cannot run session: WebDriver is not initialized.")
            return

        if self._authenticate():
            logger.info("Authentication successful. Proceeding to perform organic actions.")
            self._perform_organic_actions()
        else:
            logger.warning("Authentication failed. Organic actions will not be performed this session.")
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

            # Simulate watching a video (duration defined in HumanBehaviorSimulator)
            self.behavior.watch_video()

            # Simulate liking a video with a 65% probability
            like_probability = 0.65
            if random.random() < like_probability:
                logger.debug(f"Attempting to like video (probability: {like_probability*100}%).")
                self.behavior.like_video()
            else:
                logger.debug(f"Skipping like for this video (probability: {like_probability*100}%).")

            # Simulate scrolling
            self.behavior.random_scroll()

            # Pause between action cycles to mimic user thinking time or browsing.
            # Duration of this pause can also be made mode-dependent in HumanBehaviorSimulator.
            base_sleep_time = random.uniform(8, 15) # Base pause time
            logger.debug(f"Pausing for {base_sleep_time:.2f} seconds between action cycles.")
            time.sleep(base_sleep_time) # Consider using self.behavior.random_delay for mode-awareness

            # Optional: Add a check here to see if the bot should terminate early
            # (e.g., based on external signal, time limit, or error count).

        logger.info(f"Completed {max_views} organic action cycles for the session.")