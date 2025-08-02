"""
Módulo principal del bot para TikTok.

Este módulo define la clase TikTokBot, que encapsula la lógica para interactuar
con la plataforma TikTok, incluyendo la inicialización del driver de Selenium,
autenticación, y la ejecución de acciones orgánicas simulando comportamiento humano.
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
from core.account_manager import AccountManager

class TikTokBot:
    """
    Clase principal para el bot de TikTok.

    Gestiona la interacción con TikTok, incluyendo la configuración del navegador,
    autenticación de cuenta, y la ejecución de acciones en la plataforma.
    Utiliza AccountManager para la gestión de cuentas y HumanBehaviorSimulator
    para simular interacciones humanas realistas.
    """
    def __init__(self, _email=None, _account_details=None):
        """
        Inicializa una instancia de TikTokBot.

        Args:
            _email (str, optional): Email de la cuenta a utilizar. No se usa directamente
                                   en esta versión pero se mantiene por compatibilidad con tests.
            _account_details (dict, optional): Detalles de la cuenta. No se usa directamente
                                             en esta versión.
        """
        self.driver = self._init_driver()
        # TODO: AccountManager debería idealmente recibir un filepath o configuración.
        self.account_manager = AccountManager()
        self.proxy = None
        self.fingerprint = None
        self.behavior = HumanBehaviorSimulator(self.driver)
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from core.account_manager import CoreAccountManager
from core.behavior import HumanBehaviorSimulator
from core.logger import get_logger
from core.config_loader import ConfigLoader
from interactions.engagement import EngagementManager # Added
from config.settings import (
    DEFAULT_BOT_MODE, MAX_VIEWS_FALLBACK,
    LIKE_PROBABILITY, INTER_ACTION_CYCLE_PAUSE_RANGE_SECS
)

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
    - Loading UI selectors from an external configuration file.
    - Managing account credentials via an AccountManager.
    - Handling the authentication process on TikTok using loaded selectors.
    - Performing a series of 'organic' actions like watching videos,
      liking content, and scrolling, simulated via HumanBehaviorSimulator.

    Attributes:
        driver: The Selenium WebDriver instance used to interact with the browser.
        mode (str): The operational mode of the bot (e.g., 'safe', 'balanced').
        account_manager (CoreAccountManager): Manages retrieval of account credentials.
        behavior (HumanBehaviorSimulator): Simulates human-like interactions.
        engagement_manager (EngagementManager): Manages engagement tracking with users.
        selectors (dict): A dictionary of UI selectors loaded from selectors.json.
        shared_status (dict, optional): A dictionary for sharing status with other threads.
        status_lock (threading.Lock, optional): A lock for synchronizing access to shared_status.
        proxy (str, optional): Proxy server string (e.g., "http://host:port").
        fingerprint (str, optional): User-Agent string for browser fingerprinting.
    """
    def __init__(self, mode=DEFAULT_BOT_MODE, shared_status=None, status_lock=None, proxy=None, fingerprint=None): # Added proxy, fingerprint
        """
        Initializes the TikTokBot.

        Args:
            mode (str, optional): The operational mode for the bot.
                                  Defaults to `config.settings.DEFAULT_BOT_MODE`.
            shared_status (dict, optional): Dictionary for inter-thread status sharing.
            status_lock (threading.Lock, optional): Lock for synchronizing shared_status access.
            proxy (str, optional): Proxy server string to be used by the WebDriver.
            fingerprint (str, optional): User-Agent string for the WebDriver.
        """
        # self.logger = get_logger(f"TikTokBot.{mode}") # Alternative: instance-specific logger with mode
        logger.info(f"Initializing TikTokBot with mode: {mode}")

        self.proxy = proxy # Store proxy
        self.fingerprint = fingerprint # Store fingerprint

        if self.proxy:
            logger.info(f"TikTokBot instance configured to use proxy: {self.proxy}")
        if self.fingerprint:
            logger.info(f"TikTokBot instance configured to use fingerprint (User-Agent): {self.fingerprint}")

        self.shared_status = shared_status
        self.status_lock = status_lock
        self.session_actions_count = 0 # Initialize session action counter
        self.selectors = {} # Initialize selectors attribute
        self.engagement_manager = EngagementManager()
        logger.info("EngagementManager initialized for TikTokBot.")

        self._update_shared_status({"mode": mode, "status": "loading_config"})
        self.selectors = ConfigLoader.load_selectors("selectors.json")

        # Critical check for essential selectors after loading
        if not self.selectors or \
           not self.selectors.get("common", {}).get("login_page_url") or \
           not self.selectors.get("login_page", {}).get("username_field") or \
           not self.selectors.get("login_page", {}).get("password_field") or \
           not self.selectors.get("login_page", {}).get("submit_button"):

            logger.critical("Essential selectors (login URL, username, password, submit) not found or selectors.json failed to load. TikTokBot cannot operate.")
            self._update_shared_status({"status": "error_selector_config", "last_error": "Essential selectors missing."})
            # Ensure driver is None if selectors are missing, even if it was initialized before this check (which it isn't here)
            self.driver = None
            self.behavior = None
            return # Stop further initialization

        self._update_shared_status({"status": "initializing_webdriver"})
        self.driver = self._init_driver() # Initialize WebDriver
        self.mode = mode
        self.account_manager = CoreAccountManager() # Manages TikTok account credentials

        if self.driver:
            self.behavior = HumanBehaviorSimulator(self.driver, mode=self.mode)
            self._update_shared_status({"status": "initialized_ready"})
        else:
            # This path is taken if _init_driver() returns None
            logger.error("HumanBehaviorSimulator not initialized due to WebDriver failure.")
            self.behavior = None # Ensure behavior is None if driver is None
            # _init_driver logs its own errors, shared status updated based on self.driver check
            self._update_shared_status({
                "status": "error_webdriver_init",
                "last_error": "WebDriver failed to initialize during bot __init__."
            })
            # No need to quit driver here as it would be None

    def assign_proxy(self, proxy_value):
        """Asigna un valor de proxy al bot."""
        self.proxy = proxy_value

    def assign_fingerprint(self, fingerprint_value):
        """Asigna un valor de fingerprint al bot."""
        self.fingerprint = fingerprint_value

    def _init_driver(self):
        """
        Inicializa el driver de Selenium (Chrome) con opciones específicas.

        Configura el navegador para operar en modo headless, con un user-agent
        móvil y deshabilita la GPU y el sandbox para compatibilidad en servidores.

        Returns:
            selenium.webdriver.Chrome: Instancia del driver de Chrome configurado.
        """
        options = webdriver.ChromeOptions()
        # Common options for running in automated environments / headless
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        user_agent_string = (
            "user-agent=Mozilla/5.0 (Linux; Android 10; SM-G981B) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 "
            "Mobile Safari/537.36"
        )
        options.add_argument(user_agent_string)
        return webdriver.Chrome(options=options)

    def _authenticate(self):
        """
        Autentica el bot en TikTok utilizando una cuenta del AccountManager.

        Navega a la página de login, introduce las credenciales y envía el formulario.
        Utiliza HumanBehaviorSimulator para las interacciones.

        Returns:
            bool: True si la autenticación fue exitosa, False en caso contrario.
        """
        auth_start_time = time.monotonic()  # Track authentication duration
        account = self.account_manager.get_next_account()
        # Ensure account has 'username' and 'password' keys.
        if not account or not account.get("username") or not account.get("password"):
            logger.warning("Authentication skipped: No valid account credentials (missing username or password) found in AccountManager.")
            self._update_shared_status({
                "status": "error_no_account",
                "current_user": None, # Explicitly set current_user to None
                "last_error": "No valid account credentials (missing username or password) found."
            })
            auth_duration = time.monotonic() - auth_start_time
            logger.warning(f"Authentication check failed in {auth_duration:.2f} seconds (no valid account).")
            self._update_shared_status({"last_auth_duration": round(auth_duration, 2)})
            return False

        # Use 'username' from the account dictionary
        current_username = account.get('username')
        logger.info(f"Attempting to authenticate with account: {current_username}")
        self._update_shared_status({
            "status": "authenticating",
            "current_user": current_username,
            "last_error": None
        })

        if not self.driver or not self.behavior:
            logger.error("Authentication cannot proceed: WebDriver or HumanBehaviorSimulator not initialized.")
            self._update_shared_status({
                "status": "error_internal_bot_setup",
                "last_error": "WebDriver or BehaviorSimulator not ready for auth."
            })
            auth_duration = time.monotonic() - auth_start_time
            logger.error(f"Authentication check failed in {auth_duration:.2f} seconds (bot not ready).")
            self._update_shared_status({"last_auth_duration": round(auth_duration, 2)})
            return False

        try:
            self.driver.get("https://www.tiktok.com/login")
            self.behavior.random_delay(3, 5) # Uncommented

            # Llenar campos de login
            email_field = self.driver.find_element(By.NAME, "username")
            self.behavior.human_type(email_field, account['email']) # Uncommented

            pass_field = self.driver.find_element(By.NAME, "password")
            self.behavior.human_type(pass_field, account['password']) # Uncommented

            # Enviar formulario
            submit_btn = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            self.behavior.human_click(submit_btn) # Uncommented

            # It's crucial to add a post-login check here.
            # For example, wait for a specific element on the home page or check if the URL changed.
            # current_url = self.driver.current_url
            # if "login" not in current_url:
            # logger.info("Authentication seems successful (URL changed).")
            # else:
            # logger.warning("Authentication may have failed (still on login page or login-related URL).")
            # return False
            # For now, we assume success if no exceptions occur.
            auth_duration = time.monotonic() - auth_start_time
            logger.info(f"Authentication successful in {auth_duration:.2f} seconds.")
            self._update_shared_status({"status": "authenticated", "last_auth_duration": round(auth_duration, 2)})
            return True
        except (NoSuchElementException, TimeoutException) as specific_selenium_error:
            err_msg = f"Selenium error during auth: {specific_selenium_error}"
            auth_duration = time.monotonic() - auth_start_time
            logger.error(f"Authentication failed in {auth_duration:.2f} seconds. Reason: {err_msg}")
            self._update_shared_status({"status": "error_auth_failed", "last_error": err_msg, "last_auth_duration": round(auth_duration, 2)})
            return False
        except WebDriverException as wd_error:
            err_msg = f"WebDriver error during auth: {wd_error}"
            auth_duration = time.monotonic() - auth_start_time
            logger.error(f"Authentication failed in {auth_duration:.2f} seconds. Reason: {err_msg}")
            self._update_shared_status({"status": "error_auth_failed", "last_error": err_msg, "last_auth_duration": round(auth_duration, 2)})
            return False
        except Exception as e:
            err_msg = f"Unexpected error during auth: {e}"
            auth_duration = time.monotonic() - auth_start_time
            logger.exception(f"Authentication failed in {auth_duration:.2f} seconds. Reason: {err_msg}")
            self._update_shared_status({"status": "error_auth_failed", "last_error": err_msg, "last_auth_duration": round(auth_duration, 2)})
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
        Ejecuta una sesión completa del bot.

        Intenta autenticar y, si tiene éxito, realiza acciones orgánicas.
        """
        if self._authenticate():
            self._perform_organic_actions()
            self._update_shared_status({"status": "session_complete"}) # If actions loop completes
        else:
            logger.warning("Authentication failed. Organic actions will not be performed this session.")
            # _authenticate method should have set the appropriate error status.
        logger.info("Bot session finished.")


    def _perform_organic_actions(self):
        """
        Realiza acciones orgánicas en TikTok después de la autenticación.

        Simula ver videos, dar 'like' y hacer scroll, con pausas aleatorias
        para imitar el comportamiento humano. El número de videos a ver se
        controla mediante la variable de entorno MAX_VIEWS_PER_HOUR.
        """
        max_views = int(os.getenv("MAX_VIEWS_PER_HOUR", "50"))
        for _ in range(max_views):
            self.behavior.watch_video() # Uncommented
            # 65% de probabilidad de like
            if random.random() < 0.65: # This line itself is fine
                self.behavior.like_video() # Uncommented
            self.behavior.random_scroll() # Uncommented
            time.sleep(random.uniform(8, 15))
