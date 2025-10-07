import nltk
from nltk.corpus import stopwords

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)

class StopwordRemover:
    """Remove English stopwords"""

    def __init__(self, language="english"):
        self.stopwords = set(stopwords.words(language))

    def remove(self, tokens):
        return [tok for tok in tokens if tok.lower() not in self.stopwords]
