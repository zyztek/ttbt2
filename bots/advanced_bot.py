from core.bot import Bot
from core.logger import get_logger
from core.plugin_manager import PluginManager
import time

class AdvancedBot(Bot):
    def __init__(self, username, account_data):
        super().__init__(username, account_data)
        self.logger = get_logger(username)
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_plugin("plugins/logger_plugin.py")
        self.plugin_manager.load_plugin("plugins/custom_action.py")

    def run(self):
        self.logger.info(f"[{self.username}] Iniciando AdvancedBot con proxy {self.proxy} y fingerprint {self.fingerprint}")
        # Simula login con 3 intentos
        for intento in range(3):
            time.sleep(0.3)
            self.logger.info(f"[{self.username}] Intento de login {intento+1}")
        self.logger.success(f"[{self.username}] Login exitoso")
        # Ejecuta plugin después de login
        self.plugin_manager.execute_hook("after_login", bot=self)
        # Acción personalizada vía plugin
        self.plugin_manager.execute_hook("custom_action", bot=self)
        self.logger.info(f"[{self.username}] Finalizó ciclo avanzado")