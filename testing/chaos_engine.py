import random

class ChaosEngine:
    def __init__(self, bot):
        self.bot = bot

    def introduce_fault(self):
        # Randomly simulate a fault
        if random.random() < 0.1:
            raise Exception("Simulated random failure")