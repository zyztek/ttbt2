class AccountManager:
    def __init__(self):
        self.accounts = []

    def add_account(self, email, password):
        self.accounts.append({"email": email, "password": password})

    def get_next_account(self):
        if not self.accounts:
            return None
        return self.accounts[0]