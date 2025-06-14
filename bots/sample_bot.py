"""
Sample bot implementation for the TTBT1 framework.

This module provides a basic example of a bot that inherits from the
core `Bot` class. It demonstrates how to initialize a bot instance
and implement the `run` method to perform simulated actions.
"""
from core.bot import Bot
# To use logging instead of print, you would add:
# from core.logger import get_logger

class SampleBot(Bot):
    """
    A sample bot implementation demonstrating basic inheritance and functionality.

    This bot simulates a login process and a simple action, printing information
    about its operation, including username, account data, proxy, and fingerprint
    if assigned. It serves as a basic template or test case for the Bot base class.
    """
    def __init__(self, username, account_data):
        """
        Initializes the SampleBot.

        Args:
            username (str): The username for this bot instance.
            account_data (dict): A dictionary containing account-specific data,
                                 expected to have a "pass" key for this sample.
        """
        super().__init__(username, account_data)
        # If using a dedicated logger for this bot instance:
        # self.logger = get_logger(f"SampleBot.{self.username}")
        # For this example, we'll stick to print statements as in the original,
        # but ensuring they are in English.
        print(f"[{self.username}] SampleBot instance created.")

    def run(self):
        """
        Executes the main logic for the SampleBot.

        This method simulates a login attempt using the provided account data
        and then performs a sample action, printing details of its configuration
        (proxy, fingerprint) to the console.
        """
        print(f"[{self.username}] Starting SampleBot run...")

        # Simulate login
        if "pass" in self.account_data:
            # Accessing account_data which is an instance variable from the base class
            print(f"[{self.username}] Login successful using password: {self.account_data['pass']}")
        else:
            print(f"[{self.username}] Password not found in account_data.")

        # Simulate an action
        # This demonstrates accessing attributes (username, proxy, fingerprint)
        # inherited or set via base class methods.
        action_message = f"[{self.username}] Example action executed."
        if self.proxy: # self.proxy is from the base class
            action_message += f" Using proxy: {self.proxy}."
        else:
            action_message += " No proxy assigned."
        if self.fingerprint: # self.fingerprint is from the base class
            action_message += f" Using fingerprint: {self.fingerprint}."
        else:
            action_message += " No fingerprint assigned."
        print(action_message)
        print(f"[{self.username}] SampleBot run finished.")

# Example usage (as shown in README.md, for testing purposes if this file is run directly):
# if __name__ == "__main__":
#     # Test case 1: Bot with proxy and fingerprint
#     bot1 = SampleBot("user123", {"pass": "secretpassword"})
#     bot1.assign_proxy("http://myproxy.com:8080") # Method from base class
#     bot1.assign_fingerprint("fingerprintXYZ123") # Method from base class
#     bot1.run()
#
#     print("-" * 20)
#
#     # Test case 2: Bot without proxy/fingerprint, different account data
#     bot2 = SampleBot("user456", {"token": "another_token", "pass": "test"})
#     bot2.run()
#
#     print("-" * 20)
#
#     # Test case 3: Bot with only proxy
#     bot3 = SampleBot("user789", {"pass": "pa$$word"})
#     bot3.assign_proxy("http://anotherproxy.net:3128")
#     bot3.run()
