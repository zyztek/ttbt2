class TelegramAPI:
    def __init__(self, token):
        self.token = token

    def send_message(self, chat_id, text):
        # Integrate with python-telegram-bot or requests here
        print(f"[Telegram] {chat_id}: {text}")