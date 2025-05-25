class ReferralManager:
    def __init__(self):
        self.referrals = []

    def add_referral(self, user):
        self.referrals.append(user)