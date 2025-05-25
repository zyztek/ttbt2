class BotFactory:
    def create_bot(self, platform):
        if platform == "tiktok":
            from core.bot import TikTokBot
            return TikTokBot()
        elif platform == "youtube":
            from multiplatform.youtube_shorts_bot import YouTubeShortsBot
            return YouTubeShortsBot()
        else:
            raise ValueError("Unsupported platform")