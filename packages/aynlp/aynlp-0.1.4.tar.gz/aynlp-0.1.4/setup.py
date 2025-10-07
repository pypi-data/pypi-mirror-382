from setuptools import setup, find_packages

VERSION = '0.1.4'
DESCRIPTION = 'AYNLP: A lightweight NLP toolkit built by Ankit and Yash for tokenization, stemming, lemmatization, and more. Visit https://github.com/aijadugar/AYNLP to explore the project.'

LONG_DESCRIPTION = """
AYNLP (Advanced Yet Simple NLP) is a modular and lightweight Python toolkit designed to make 
Natural Language Processing (NLP) accessible, fun, and powerful. With AYNLP, you can:

- Tokenize text and filter stopwords
- Perform stemming and lemmatization
- Tag parts-of-speech (POS) and extract named entities (NER)
- Analyze sentiment using multiple approaches

The library is **easy to use**, highly **extensible**, and ideal for educational, research, and open-source projects.

📌 **Why Contribute?**
- Help enhance NLP functionalities and add new features
- Improve existing modules like tokenization, POS tagging, or sentiment analysis
- Optimize code performance and expand compatibility with other NLP libraries
- Report issues, suggest improvements, and participate in shaping the roadmap of a growing open-source project

💡 **Get Started**
Visit the GitHub repository: [AYNLP](https://github.com/aijadugar/AYNLP) to fork the project, raise issues, or contribute code. Every contribution helps the community and strengthens the toolkit for everyone.

Whether you are a student, researcher, or developer, AYNLP offers a playground for learning and contributing to real-world NLP projects.

---

## ⚡ How to Use AYNLP

```python
from aynlp import AYNLP

# Initialize the pipeline
aynlp = AYNLP()

# Analyze text
result = aynlp.analyze("The yesterday's festival was awesome!")

# Print the results
print(result)

"""

setup(
    name="aynlp",
    version=VERSION,
    author="Ankit Bari <ankitbari@zohomail.in>, Yash Kerkar <kerkaryash5@gmail.com>",
    author_email="ankitbari@zohomail.in, kerkaryash5@gmail.com",  
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
    "numpy>=1.26.0,<2.0",
    "scipy>=1.11.0,<1.28.0",
    "spacy>=3.7.0",
    "nltk>=3.8.1",
    "tabulate>=0.9.0",
    "textblob>=0.17.1"
    ],
    python_requires='>=3.7',
    license="MIT",
    keywords=[
    'python', 
    'aynlp', 
    'nlp', 
    'natural-language-processing', 
    'tokenization', 
    'lemmatization', 
    'stemming', 
    'pos-tagging', 
    'ner', 
    'sentiment-analysis', 
    'text-processing', 
    'Ankit Bari', 
    'Yash Kerkar'
    ],
    url="https://github.com/aijadugar/AYNLP", 
    classifiers=[
        "Development Status :: 3 - Alpha", 
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)