class EngagementManager:
    def __init__(self):
        self.engaged_users = set()

    def engage_user(self, user_id):
        self.engaged_users.add(user_id)