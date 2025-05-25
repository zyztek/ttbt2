class CommentManager:
    def __init__(self):
        self.comments = []

    def add_comment(self, comment):
        self.comments.append(comment)

    def get_comments(self):
        return self.comments