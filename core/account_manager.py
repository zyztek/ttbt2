"""
Manages TikTok accounts for the bot.

This module provides a simple in-memory mechanism for storing and retrieving
TikTok account credentials. In its current version, it holds accounts in a list
and provides a basic way to access them. Future enhancements could include
database integration, account rotation, and status tracking.
"""

class CoreAccountManager:
    """
    A simple in-memory manager for user accounts.

    Attributes:
        accounts (list): A list of dictionaries, where each dictionary
                         represents an account and contains 'email' and
                         'password' keys.
    """
    def __init__(self):
        """
        Initializes the CoreAccountManager with an empty list of accounts.
        """
        self.accounts = []  # Initialize an empty list to store account details

    def add_account(self, email, password):
        """
        Adds a new account to the internal list.

        Args:
            email (str): The email address associated with the TikTok account.
            password (str): The password for the TikTok account.

        Raises:
            ValueError: If email or password are not strings.
        """
        if not isinstance(email, str) or not isinstance(password, str):
            # Simple validation, could be expanded (e.g., email format check)
            raise ValueError("Email and password must be strings.")

        account_details = {"email": email, "password": password}
        self.accounts.append(account_details)
        # Consider adding logging here if a logger is passed or globally available.
        # For example: logger.info(f"Account added for email: {email}")

    def get_next_account(self):
        """
        Retrieves an account from the list.

        In this basic implementation, it always returns the first account
        if the list of accounts is not empty. If the list is empty,
        it returns None. This method could be extended to support
        account rotation or selection based on various criteria.

        Returns:
            dict or None: A dictionary containing 'email' and 'password' of an
                          account, or None if no accounts are available.
        """
        if not self.accounts:
            # No accounts have been added yet.
            return None
        # Currently, always returns the first account.
        # This is a placeholder for more sophisticated account selection logic
        # (e.g., round-robin, least recently used, etc.).
        return self.accounts[0]
