import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

# ensure required NLTK data
for pkg in ["wordnet", "omw-1.4", "averaged_perceptron_tagger"]:
    try:
        nltk.data.find(f"corpora/{pkg}")
    except LookupError:
        nltk.download(pkg, quiet=True)

class Lemmatizer:
    """NLTK WordNet lemmatizer"""

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def _get_wordnet_pos(self, treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN

    def lemmatize(self, word, pos_tag=None):
        pos = self._get_wordnet_pos(pos_tag) if pos_tag else wordnet.NOUN
        return self.lemmatizer.lemmatize(word, pos=pos)

    def lemmatize_sentence(self, tokens):
        tagged = nltk.pos_tag(tokens)
        return [self.lemmatize(word, tag) for word, tag in tagged]
