from nltk.stem import PorterStemmer

class Stemmer:
    """NLTK Porter Stemmer"""

    def __init__(self):
        self.stemmer = PorterStemmer()

    def stem(self, word):
        return self.stemmer.stem(word)
