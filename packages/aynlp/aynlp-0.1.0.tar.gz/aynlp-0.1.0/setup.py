from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.1.0'
DESCRIPTION = 'AYNLP: A lightweight NLP toolkit built by Ankit and Yash for tokenization, stemming, lemmatization, and more.'
LONG_DESCRIPTION = 'A package to perform multiple NLP-related tasks like tokenization, lemmatization, POS tagging, NER, and sentiment analysis.'

setup(
    name="aynlp",
    version=VERSION,
    author="Ankit and Yash",
    author_email="ankit.s238247105@vcet.edu.in, yash.s238267105@vcet.edu.in",  
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "nltk>=3.8.1",
        "spacy>=3.7.0",
        "tabulate-0.9.0",
    ],
    python_requires='>=3.7',
    license="MIT",
    keywords=['python', 'aynlp', 'nlp', 'tokenization', 'lemmatization', 'Ankit', 'Yash'],
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