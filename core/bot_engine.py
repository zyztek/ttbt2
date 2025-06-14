"""
Módulo del motor de bots (BotEngine).

Proporciona la clase BotEngine, responsable de gestionar múltiples instancias de bots,
inicializarlas con configuraciones específicas (cuentas, proxies, fingerprints) y
orquestar su ejecución.
"""
from core.bot import TikTokBot # Import TikTokBot

class BotEngine:
    """
    Orquesta la creación, configuración y ejecución de múltiples instancias de bots.

    Utiliza un diccionario de cuentas y gestores de proxies y fingerprints para
    preparar cada bot antes de ejecutar su sesión principal.
    """
    def __init__(self, accounts, proxy_manager, fingerprint_manager):
        """
        Inicializa el BotEngine.

        Args:
            accounts (dict): Un diccionario donde las claves son identificadores de cuenta
                             (ej. emails) y los valores son diccionarios con detalles
                             de la cuenta (ej. contraseñas).
            proxy_manager: Una instancia de un gestor de proxies, que debe tener un
                           método `get_random_active_proxy()`.
            fingerprint_manager: Una instancia de un gestor de fingerprints, que debe
                                 tener un método `get_fingerprint()`.
        """
        self.accounts = accounts
        self.proxy_manager = proxy_manager
        self.fingerprint_manager = fingerprint_manager
        self.bots = []

    def initialize_bots(self):
        """
        Crea e inicializa instancias de TikTokBot para cada cuenta.

        Itera sobre el diccionario `self.accounts`. Para cada cuenta, crea una
        instancia de `TikTokBot`, le asigna un proxy obtenido del `proxy_manager`
        y un fingerprint del `fingerprint_manager`. Los bots configurados
        se almacenan en la lista `self.bots`.

        Si `self.accounts` no es un diccionario, imprime un mensaje de error
        y retorna prematuramente, dejando `self.bots` vacío.
        """
        if not isinstance(self.accounts, dict):
            # Or raise an error, or log
            print("Accounts data is not in the expected dictionary format.")
            return

        for email, account_details in self.accounts.items():
            bot = TikTokBot(_email=email, _account_details=account_details)

            proxy = self.proxy_manager.get_random_active_proxy()
            if proxy: # Ensure a proxy was returned
                bot.assign_proxy(proxy)

            fingerprint = self.fingerprint_manager.get_fingerprint()
            if fingerprint: # Ensure a fingerprint was returned
                bot.assign_fingerprint(fingerprint)

            self.bots.append(bot)

    def run(self):
        """
        Ejecuta las sesiones para todos los bots gestionados.

        Primero se asegura de que los bots hayan sido inicializados llamando a
        `initialize_bots()` si la lista `self.bots` está vacía. Luego, itera
        sobre cada bot en `self.bots` y llama a su método `run_session()`.
        """
        if not self.bots:
            self.initialize_bots() # Initialize if not already done

        for bot in self.bots:
            bot.run_session()
