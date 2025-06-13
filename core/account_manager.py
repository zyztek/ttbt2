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
        """
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
