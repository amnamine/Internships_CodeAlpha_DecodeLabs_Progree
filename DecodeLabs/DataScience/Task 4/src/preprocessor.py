import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Ensure required NLTK resources are available
for pkg in ['stopwords', 'wordnet', 'punkt', 'punkt_tab', 'omw-1.4']:
    try:
        nltk.data.find(f'corpora/{pkg}')
    except LookupError:
        try:
            nltk.data.find(f'tokenizers/{pkg}')
        except LookupError:
            nltk.download(pkg, quiet=True)


class TextPreprocessor:
    """
    Strict Text Pre-Processing pipeline for NLP sentiment analysis:
    - HTML tag stripping
    - Special characters and punctuation removal
    - Lowercasing
    - Negation-aware stop words filtering
    - Lemmatization using WordNet Lemmatizer
    """

    def __init__(self, preserve_negations=True):
        self.lemmatizer = WordNetLemmatizer()
        
        # Load English stopwords from NLTK
        stop_words_set = set(stopwords.words('english'))
        
        # In sentiment analysis, words like 'not', 'no', 'never', 'nor' dramatically flip sentiment.
        # Preserving them ensures high classification quality.
        if preserve_negations:
            negation_words = {
                'not', 'no', 'nor', 'neither', 'never', "didn't", "wasn't", 
                "weren't", "isn't", "aren't", "couldn't", "wouldn't", "shouldn't",
                "doesn't", "don't", "haven't", "hasn't", "hadn't", "won't"
            }
            stop_words_set = stop_words_set - negation_words
            
        self.stop_words = stop_words_set

    def clean_html_and_urls(self, text: str) -> str:
        """Removes HTML tags (like <br />) and URLs."""
        if not isinstance(text, str):
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Remove URLs
        text = re.sub(r'http\S+|www\.\S+', ' ', text)
        return text

    def clean_special_characters(self, text: str) -> str:
        """Keeps only alphabetical characters, basic spaces and handles contractions."""
        # Replace non-alphanumeric with spaces (keeping words)
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        # Collapse multiple spaces into single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def preprocess_text(self, text: str) -> str:
        """
        Executes the full preprocessing pipeline on a single text string:
        HTML clean -> Lowercase -> Clean special chars -> Tokenize -> Stopword removal -> Lemmatize
        """
        if not isinstance(text, str):
            return ""

        # 1. Clean HTML & URLs
        text = self.clean_html_and_urls(text)

        # 2. Lowercase
        text = text.lower()

        # 3. Clean special characters & digits
        text = self.clean_special_characters(text)

        # 4. Tokenization (fast splitting or word_tokenize)
        tokens = text.split()

        # 5. Stopword removal & Lemmatization
        processed_tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words and len(token) > 1
        ]

        return " ".join(processed_tokens)

    def transform_series(self, series, verbose=False):
        """Processes a pandas Series of texts with progress indication if requested."""
        if verbose:
            from tqdm import tqdm
            return series.apply(self.preprocess_text)
        return series.apply(self.preprocess_text)
