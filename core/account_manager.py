import json
import os

class AccountManager:
    def __init__(self, filepath=None):
        self.accounts = {}
        if filepath and os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.accounts = json.load(f)
            except (IOError, json.JSONDecodeError):
                # Log error here if logging is set up
                self.accounts = {}

    def add_account(self, email, password):
        # Assuming email is unique and used as a key
        self.accounts[email] = {"password": password}

    def get_next_account(self):
        if not self.accounts:
            return None
        # Return the details of the first account found (key-value pair)
        # For consistency, let's sort keys to always get the "first" by some order
        # This makes it somewhat predictable, though dictionary order is not guaranteed
        # across all Python versions without explicit sorting.
        if isinstance(self.accounts, dict) and self.accounts:
            first_email = sorted(self.accounts.keys())[0]
            # The original structure was a list of dicts like {"email": email, "password": password}
            # The new structure is a dict like {email: {"password": password}}
            # To maintain a somewhat similar output for get_next_account for now,
            # let's reconstruct that, or decide on a new format.
            # For this step, let's return the email and its password dict.
            # A better approach would be to return a consistent object or dict.
            return {"email": first_email, "password": self.accounts[first_email]["password"]}
        return None