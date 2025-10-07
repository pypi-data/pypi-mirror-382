import nltk

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

class Tokenizer:
    """Simple word tokenizer"""

    def tokenize(self, text):
        return nltk.word_tokenize(text)
