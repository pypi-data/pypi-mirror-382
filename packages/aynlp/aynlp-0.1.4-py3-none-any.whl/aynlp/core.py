from .tokenizer import Tokenizer
from .lemmatizer import Lemmatizer
from .stemmer import Stemmer
from .stopwords import StopwordRemover
from .pos_tagger import POSTagger
from .ner import NER
from .sentiment import SentimentAnalyzer
from tabulate import tabulate


class AYNLP:
    """Unified NLP pipeline with table output 🎯"""

    def __init__(self):
        self.tokenizer = Tokenizer()
        self.stopword_remover = StopwordRemover()
        self.lemmatizer = Lemmatizer()
        self.stemmer = Stemmer()
        self.pos_tagger = POSTagger()
        self.ner = NER()
        self.sentiment_analyzer = SentimentAnalyzer()

    def analyze(self, text):
        tokens = self.tokenizer.tokenize(text)
        filtered_tokens = self.stopword_remover.remove(tokens)
        pos_tags = self.pos_tagger.tag(tokens)
        lemmas = [self.lemmatizer.lemmatize(tok, tag) for tok, tag in pos_tags]
        stems = [self.stemmer.stem(tok) for tok in tokens]
        entities = self.ner.extract_entities(tokens)
        sentiment = self.sentiment_analyzer.analyze(text)

        data = [
            ["🧩 Tokens", ", ".join(tokens)],
            ["🚫 Filtered Tokens", ", ".join(filtered_tokens)],
            ["🔤 Lemmas", ", ".join(lemmas)],
            ["🌱 Stems", ", ".join(stems)],
            ["🏷️ POS Tags", ", ".join([f"{w}/{t}" for w, t in pos_tags])],
            ["🧠 Entities", ", ".join([f"{e} ({t})" for e, t in entities]) if entities else "—"],
            ["💬 Sentiment",
             "😊 Positive" if sentiment == "positive"
             else ("😐 Neutral" if sentiment == "neutral" else "😞 Negative")],
        ]

        table = tabulate(data, headers=["🔍 Feature", "📊 Result"], tablefmt="fancy_grid")
        return table
