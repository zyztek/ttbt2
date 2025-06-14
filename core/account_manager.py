"""
Módulo para la gestión de cuentas de usuario.

Proporciona una clase AccountManager que permite cargar cuentas desde un archivo JSON,
añadir nuevas cuentas y obtener la siguiente cuenta disponible. Las cuentas
se almacenan como un diccionario donde la clave es el email del usuario.
"""
import json
import os

class AccountManager:
    """
    Gestiona las cuentas de usuario, permitiendo la carga desde archivo y
    la adición y recuperación de cuentas.
    """
    def __init__(self, filepath=None):
        """
        Inicializa el gestor de cuentas.

        Si se proporciona un `filepath` y el archivo existe, intenta cargar
        las cuentas desde este archivo JSON. En caso de error o si no se
        proporciona el archivo, inicializa con un diccionario de cuentas vacío.

        Args:
            filepath (str, optional): Ruta al archivo JSON de cuentas.
                                      Por defecto es None.
        """
        self.accounts = {}
        if filepath and os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.accounts = json.load(f)
            except (IOError, json.JSONDecodeError):
                # Log error here if logging is set up
                self.accounts = {}

    def add_account(self, email, password):
        """
        Añade una nueva cuenta o actualiza una existente.

        Utiliza el email como clave única para almacenar los detalles de la cuenta.
        Actualmente, solo almacena la contraseña.

        Args:
            email (str): El email de la cuenta.
            password (str): La contraseña de la cuenta.
        """
        # Assuming email is unique and used as a key
        self.accounts[email] = {"password": password}

    def get_next_account(self):
        """
        Obtiene los detalles de la "siguiente" cuenta disponible.

        Actualmente, si hay cuentas, devuelve la primera cuenta según el orden
        de las claves de email ordenadas alfabéticamente. Retorna un diccionario
        con el email y la contraseña, o None si no hay cuentas.

        Returns:
            dict or None: Un diccionario con "email" y "password" de la cuenta,
                          o None si no hay cuentas disponibles.
Manages TikTok accounts for the bot.

This module provides a simple in-memory mechanism for storing and retrieving
TikTok account credentials. It now loads account data from a JSON file
by default, using ConfigLoader. Future enhancements could include
database integration, account rotation, and status tracking.
"""
from core.config_loader import ConfigLoader # Added
from core.logger import get_logger # Added

# Initialize logger for this module
account_manager_logger = get_logger(__name__)

class CoreAccountManager:
    """
    Manages user accounts, loading them from a JSON file and providing
    basic in-memory status tracking for each account.

    Attributes:
        accounts (list): A list of dictionaries, where each dictionary
                         represents an account. Each account dict contains
                         'username', 'password', 'full_details', 'status',
                         and 'status_details'.
        filepath (str): The path to the accounts file.
        current_account_index (int): The index of the next account to be returned by
                                     `get_next_account()`.
    """
    def __init__(self, filepath="accounts.json"):
        """
        Initializes the CoreAccountManager and loads accounts from a file.

        Args:
            filepath (str, optional): The path to the JSON file containing
                                      account data. Defaults to "accounts.json".
        """
        self.accounts = []  # Initialize an empty list to store account details
        self.filepath = filepath
        self._load_accounts_from_file(self.filepath)

        if self.accounts:
            account_manager_logger.info(f"Successfully loaded {len(self.accounts)} accounts from '{self.filepath}'.")
        else:
            account_manager_logger.warning(f"No accounts loaded from '{self.filepath}'. The account list is empty.")

        self.current_account_index = 0 # Initialize index for account cycling

    def _load_accounts_from_file(self, filepath):
        """
        Loads account data from a specified JSON file.

        The JSON file is expected to have a structure where keys are usernames
        and values are dictionaries containing account details (e.g., {"pass": "secret", ...}).

        Args:
            filepath (str): The path to the JSON file.
        """
        account_manager_logger.info(f"Attempting to load accounts from: {filepath}")
        raw_data = ConfigLoader.load(filepath) # ConfigLoader.load handles file not found, JSON errors

        if not raw_data: # Handles empty dict if file was empty or failed to load/parse
            account_manager_logger.warning(f"No data or invalid data found in accounts file: {filepath}")
            return

        if not isinstance(raw_data, dict):
            account_manager_logger.error(f"Account data in '{filepath}' is not a dictionary (object) as expected. Found type: {type(raw_data)}.")
            return

        processed_count = 0
        for username, account_details in raw_data.items():
            if not isinstance(account_details, dict):
                account_manager_logger.warning(f"Skipping account '{username}': details are not a dictionary. Found: {type(account_details)}")
                continue

            password = account_details.get("pass") # Common key for password in many configs
            if password is None: # Could also check for empty string if that's invalid
                # If 'pass' is not found, try 'password' as an alternative common key
                password = account_details.get("password")

            if password is not None: # Ensure password (from 'pass' or 'password') is found
                self.accounts.append({
                    "username": username,
                    "password": str(password), # Ensure password is a string
                    "full_details": account_details, # Store all original details
                    "status": "new", # Initialize status for newly loaded accounts
                    "status_details": {} # Initialize empty dict for additional status info
                })
                processed_count += 1
            else:
                account_manager_logger.warning(f"Skipping account '{username}': 'pass' or 'password' key not found in account details or is null.")

        account_manager_logger.info(f"Processed {processed_count} accounts from '{filepath}'.")


    def add_account(self, username, password, **kwargs):
        """
        Adds a new account to the internal list.
        Note: This method adds to the in-memory list. It does not currently
        save back to the accounts.json file.

        Args:
            username (str): The username for the account.
            password (str): The password for the account.
            **kwargs: Additional details for the account, stored in 'full_details'.

        Raises:
            ValueError: If username or password are not strings.
        """
        if not isinstance(username, str) or not isinstance(password, str):
            account_manager_logger.error("Failed to add account: username and password must be strings.")
            raise ValueError("Username and password must be strings.")

        # Merge explicit username/password with other details from kwargs for full_details
        full_details = {"pass": password, **kwargs} # Prioritize provided password for 'pass' key

        account_data = {
            "username": username,
            "password": password,
            "full_details": full_details,
            "status": "new", # Initialize status for manually added accounts
            "status_details": {}
        }
        self.accounts.append(account_data)
        account_manager_logger.info(f"Account for '{username}' added to in-memory list with 'new' status.")


    def get_next_account(self):
        """
        Retrieves the next account from the list in a cyclic manner.

        Each call to this method will return the next account in the list.
        If all accounts have been returned once, subsequent calls will return `None`
        until `reset_account_cycle()` is called. The returned dictionary includes
        account credentials, full details, and current status information.

        Returns:
            dict or None: A dictionary representing an account (including 'username',
                          'password', 'full_details', 'status', 'status_details').
                          Returns `None` if no accounts are loaded or if all
                          accounts have been cycled through.
        """
        if not self.accounts:
            account_manager_logger.warning("get_next_account called but no accounts are loaded.")
            return None

        if self.current_account_index < len(self.accounts):
            account_to_return = self.accounts[self.current_account_index]
            self.current_account_index += 1
            account_manager_logger.debug(
                f"Returning account '{account_to_return.get('username')}' (index {self.current_account_index - 1}). "
                f"Next index: {self.current_account_index}."
            )
            return account_to_return
        else:
            account_manager_logger.info("All accounts have been cycled through. Call reset_account_cycle() to start over.")
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

    def reset_account_cycle(self):
        """
        Resets the account cycle index to 0.

        This allows `get_next_account()` to start returning accounts from the
        beginning of the list again.
        """
        account_manager_logger.info("Resetting account cycle. Next call to get_next_account() will start from the first account.")
        self.current_account_index = 0

    def update_account_status(self, username, new_status, status_info=None):
        """
        Updates the status and status_details of a specific account.

        Args:
            username (str): The username of the account to update.
            new_status (str): The new status string (e.g., "active", "banned", "cooldown").
            status_info (dict, optional): A dictionary containing additional details
                                          related to the status update. This will be
                                          merged into the existing 'status_details'
                                          of the account. Defaults to None.

        Returns:
            bool: True if the account was found and updated, False otherwise.
        """
        for account in self.accounts:
            if account.get("username") == username:
                account["status"] = new_status
                log_message = f"Status for account '{username}' updated to '{new_status}'."
                if isinstance(status_info, dict):
                    # Merge new status_info into existing status_details
                    account.setdefault("status_details", {}).update(status_info)
                    log_message += f" Details: {status_info}"
                elif status_info is not None:
                    # If status_info is not a dict but provided, store it under a default key
                    account.setdefault("status_details", {})["message"] = str(status_info)
                    log_message += f" Message: {status_info}"

                account_manager_logger.info(log_message)
                return True

        account_manager_logger.warning(f"Attempted to update status for account '{username}', but account was not found.")
        return False
