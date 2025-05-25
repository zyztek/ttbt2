class NLPProcessor:
    def __init__(self):
        pass

    def get_keywords(self, text):
        # Very basic keyword extraction (replace with spaCy, NLTK, etc. for real use)
        return [w for w in text.split() if len(w) > 3]