import nltk

class POSTagger:
    """POS Tagger using NLTK"""

    def tag(self, tokens):
        return nltk.pos_tag(tokens)
