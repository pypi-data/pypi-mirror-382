# 🧩 AYNLP - Advanced Yet Simple NLP Toolkit

**AYNLP** is a lightweight, modular Natural Language Processing (NLP) library built for educational, research, and open-source projects.  
It unifies core NLP components - Tokenization, Lemmatization, POS tagging, Named Entity Recognition, and Sentiment Analysis - into a single, easy-to-use pipeline.

---

## 🚀 Features

✅ **Tokenizer** - Splits text into structured tokens  
✅ **Stopword Remover** - Filters out common stopwords  
✅ **Lemmatizer** - Converts words to their base form  
✅ **Stemmer** - Performs root-word stemming  
✅ **POS Tagger** - Identifies grammatical roles  
✅ **NER** - Extracts named entities (people, places, etc.)  
✅ **Sentiment Analyzer** - Detects text polarity (positive, neutral, negative)  
✅ **Beautiful Output** - Displays classical table results with emojis 🧠📊

---

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/aijadugar/AYNLP.git
cd AYNLP

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

>>>from aynlp import AYNLP

>>>aynlp = AYNLP()
>>>print(aynlp.analyze("The yesterdays festival was awesome."))

# Output

╒══════════════════╤══════════════════════════════════════════════════════════╕
│ 🔍 Feature       │ 📊 Result                                                │
╞══════════════════╪══════════════════════════════════════════════════════════╡
│ 🧩 Tokens        │ The, yesterdays, festival, was, awesome, .               │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ 🚫 Filtered ...  │ yesterdays, festival, awesome, .                         │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ 🔤 Lemmas        │ The, yesterday, festival, be, awesome, .                 │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ 🌱 Stems         │ the, yesterday, festiv, wa, awesom, .                    │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ 🏷️ POS Tags      │ The/DT, yesterdays/NNS, festival/NN, was/VBD, awesome/JJ│
├──────────────────┼──────────────────────────────────────────────────────────┤
│ 🧠 Entities      │ —                                                        │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ 💬 Sentiment     │ 😊 Positive                                              │
╘══════════════════╧══════════════════════════════════════════════════════════╛

