import spacy

class NER:
    """Named Entity Recognition using spaCy"""

    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            from spacy.cli import download
            download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def extract_entities(self, text_or_tokens):
        if isinstance(text_or_tokens, list):
            text = " ".join(text_or_tokens)
        else:
            text = text_or_tokens
        doc = self.nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]
