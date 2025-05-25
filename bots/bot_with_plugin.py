from core.bot import Bot
from core.logger import get_logger
from core.plugin_manager import PluginManager

class BotWithPlugin(Bot):
    def __init__(self, username, account_data):
        super().__init__(username, account_data)
        self.logger = get_logger(username)
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_plugin("plugins/logger_plugin.py")

    def run(self):
        self.logger.info(f"Login... {self.username}")
        # ... login logic ...
        self.plugin_manager.execute_hook("after_login", bot=self)