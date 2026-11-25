from sklearn.feature_extraction.text import TfidfVectorizer
import joblib


class TextVectorizer:
    """
    Handles converting preprocessed text into numerical mathematical arrays using TF-IDF.
    Supports n-grams (unigrams, bigrams), max features, and sublinear term frequency scaling.
    """

    def __init__(self, max_features=10000, ngram_range=(1, 2), min_df=2, max_df=0.85):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.max_df = max_df
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            max_df=self.max_df,
            sublinear_tf=True
        )

    def fit_transform(self, raw_documents):
        """Fits TF-IDF on training corpus and returns sparse TF-IDF matrix."""
        return self.vectorizer.fit_transform(raw_documents)

    def transform(self, raw_documents):
        """Transforms new text documents using learned vocabulary and IDF weights."""
        return self.vectorizer.transform(raw_documents)

    def get_feature_names(self):
        """Returns array of feature names (words / n-grams)."""
        return self.vectorizer.get_feature_names_out()

    def save(self, filepath: str):
        """Saves vectorizer instance to disk."""
        joblib.dump(self.vectorizer, filepath)

    @classmethod
    def load(cls, filepath: str):
        """Loads vectorizer instance from disk."""
        instance = cls()
        instance.vectorizer = joblib.load(filepath)
        return instance
