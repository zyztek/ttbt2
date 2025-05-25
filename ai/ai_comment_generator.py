import random

class AICommentGenerator:
    def __init__(self):
        self.sample_comments = [
            "Amazing video! 🔥",
            "Loved this content, keep it up!",
            "So creative, followed!",
            "This made my day! 😂",
            "You deserve more views!"
        ]

    def generate_comment(self, context=None):
        # If context-aware AI is needed, integrate with an NLP model here
        return random.choice(self.sample_comments)