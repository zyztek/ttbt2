from core.bot import TikTokBot # Import TikTokBot

class BotEngine:
    def __init__(self, accounts, proxy_manager, fingerprint_manager):
        self.accounts = accounts
        self.proxy_manager = proxy_manager
        self.fingerprint_manager = fingerprint_manager
        self.bots = []

    def initialize_bots(self):
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
        if not self.bots:
            self.initialize_bots() # Initialize if not already done

        for bot in self.bots:
            bot.run_session()
