class BotEngine:
    def __init__(self, bot):
        self.bot = bot

    def run(self):
        self.bot.run_session()