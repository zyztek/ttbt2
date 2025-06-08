"""
Advanced bot implementation for the TTBT1 framework.

This module provides an example of a more complex bot that inherits from
the core `Bot` class. It showcases features such as:
- Per-instance logging.
- Integration with a PluginManager to load and execute plugins.
- Simulated multi-attempt login and execution of plugin hooks.
"""
from core.bot import Bot
from core.logger import get_logger
from core.plugin_manager import PluginManager
import time

class AdvancedBot(Bot):
    """
    An advanced bot implementation demonstrating features like logging and plugins.

    Inherits from the base `Bot` class and extends it with its own logger,
    a plugin manager, and a more complex `run` logic that simulates
    multiple login attempts and executes plugin hooks.

    Attributes:
        logger: An instance-specific logger named using the bot's username.
        plugin_manager (PluginManager): Manages loading and execution of plugins.
        username (str): Inherited from `Bot`. Username for the bot.
        account_data (dict): Inherited from `Bot`. Account-specific data.
        proxy (str, optional): Inherited from `Bot`. Proxy string, if assigned via `assign_proxy`.
        fingerprint (str, optional): Inherited from `Bot`. Fingerprint string, if assigned via `assign_fingerprint`.
    """
    def __init__(self, username, account_data):
        """
        Initializes the AdvancedBot.

        Args:
            username (str): The username for this bot instance. This is also used
                            as part of the logger's name.
            account_data (dict): A dictionary containing account-specific data.
        """
        super().__init__(username, account_data)
        # Initialize an instance-specific logger
        self.logger = get_logger(f"AdvancedBot.{username}")
        self.logger.info(f"AdvancedBot instance created for user '{username}'.")

        self.plugin_manager = PluginManager()
        self.logger.info("PluginManager initialized.")

        # Example of loading plugins.
        # These paths are relative to the project root or where Python executes.
        # Plugins would typically define hooks like 'after_login' or 'custom_action'.
        try:
            # Assuming plugins are located in a 'plugins' directory accessible from the project root
            self.plugin_manager.load_plugin("plugins/logger_plugin.py") # Example plugin
            self.plugin_manager.load_plugin("plugins/custom_action.py") # Another example plugin
            self.logger.info("Attempted to load standard plugins (logger_plugin.py, custom_action.py).")
        except FileNotFoundError as fnf_error:
            self.logger.warning(f"Could not load a plugin, file not found: {fnf_error}. Ensure plugin paths are correct.")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while loading plugins: {e}")

    def run(self):
        """
        Executes the main logic for the AdvancedBot.

        This method simulates a multi-attempt login process. If successful,
        it executes hooks for loaded plugins, such as 'after_login' and
        a 'custom_action'. It logs its operations using its instance-specific logger,
        including information about any assigned proxy and fingerprint.
        """
        self.logger.info(
            f"Starting AdvancedBot run for user '{self.username}'. "
            f"Proxy: '{self.proxy if self.proxy else "Not set"}', "
            f"Fingerprint: '{self.fingerprint if self.fingerprint else "Not set"}'"
        )

        # Simulate login with up to 3 attempts
        login_successful = False
        max_login_attempts = 3
        for attempt in range(max_login_attempts):
            time.sleep(0.3) # Simulate network delay or processing time
            self.logger.info(f"Login attempt {attempt + 1}/{max_login_attempts} for user '{self.username}'.")
            # In a real scenario, actual login logic (e.g., web interaction) would be here.
            # For this example, we'll assume success on the final attempt for demonstration.
            if attempt == max_login_attempts - 1:
                login_successful = True
                break

        if login_successful:
            self.logger.success(f"Login successful for user '{self.username}'.") # Using logger.success for positive outcome

            # Execute plugin hook after successful login
            self.logger.debug("Executing 'after_login' plugin hook.")
            # Pass the bot instance itself to plugins, so they can interact with it if needed
            self.plugin_manager.execute_hook("after_login", bot=self)

            # Execute a custom action via plugin system
            self.logger.debug("Executing 'custom_action' plugin hook.")
            self.plugin_manager.execute_hook("custom_action", bot=self)
        else:
            self.logger.error(f"Login failed for user '{self.username}' after {max_login_attempts} attempts.")

        self.logger.info(f"AdvancedBot run finished for user '{self.username}'.")

# Example usage (for testing purposes if this file is run directly):
# if __name__ == "__main__":
#     # Test case 1: Bot with proxy and fingerprint
#     adv_bot1 = AdvancedBot("AdvUser001", {"api_key": "some_key_example"})
#     adv_bot1.assign_proxy("http://advancedproxy.example.com:9090") # Method from base Bot class
#     adv_bot1.assign_fingerprint("advancedFingerprintABC123")    # Method from base Bot class
#     adv_bot1.run()
#
#     print("-" * 30)
#
#     # Test case 2: Bot without proxy/fingerprint, different account data
#     adv_bot2 = AdvancedBot("AdvUser002", {"session_token": "example_token"})
#     adv_bot2.run()
#
#     print("-" * 30)
#
#     # Test case 3: Bot with only fingerprint
#     adv_bot3 = AdvancedBot("AdvUser003", {})
#     adv_bot3.assign_fingerprint("anotherFingerprintDEF456")
#     adv_bot3.run()
