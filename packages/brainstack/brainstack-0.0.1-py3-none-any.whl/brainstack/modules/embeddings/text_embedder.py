import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from typing import List, Tuple, Dict, Union
import joblib
import nltk
from nltk.corpus import stopwords as nltk_stopwords

class TextEmbedder:
    """Lightweight TF-IDF text embedder with optional character n-grams."""
    
    def __init__(self, ngram_range: Tuple[int, int] = (1, 2), char_ngrams: bool = False, 
                 max_features: int = 5000, stopwords: Union[str, List[str]] = 'english'):
        """Initialize the embedder with TF-IDF parameters.

        Args:
            ngram_range: Tuple of (min_n, max_n) for word n-grams.
            char_ngrams: If True, include character n-grams (3,5) in features.
            max_features: Maximum number of features to keep.
            stopwords: Stopwords list or 'english' for NLTK stopwords.
        """
        # Ensure stopwords are downloaded
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        # Set stopwords
        self.stopwords = nltk_stopwords.words('english') if stopwords == 'english' else stopwords
        
        # Word-based TF-IDF vectorizer
        self.word_vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            max_features=max_features // 2 if char_ngrams else max_features,
            stop_words=self.stopwords,
            lowercase=True,
            token_pattern=r'(?u)\b\w+\b',  # Simple word tokenization
            dtype=np.float32
        )
        
        # Character-based TF-IDF vectorizer (optional)
        self.char_vectorizer = None
        if char_ngrams:
            self.char_vectorizer = TfidfVectorizer(
                analyzer='char',
                ngram_range=(3, 5),
                max_features=max_features // 2,
                lowercase=True,
                dtype=np.float32
            )
        
        self.is_fitted = False
        self.feature_names: List[str] = []

    def fit(self, corpus: List[str]) -> 'TextEmbedder':
        """Fit the vectorizer(s) on a corpus of texts.

        Args:
            corpus: List of text strings to fit on.

        Returns:
            Self, fitted embedder.
        """
        # Filter out empty strings to avoid issues
        corpus = [text for text in corpus if text.strip()]
        if not corpus:
            raise ValueError("Corpus is empty or contains only empty strings")
        
        # Fit word vectorizer
        self.word_vectorizer.fit(corpus)
        self.feature_names = self.word_vectorizer.get_feature_names_out().tolist()
        
        # Fit char vectorizer if enabled
        if self.char_vectorizer:
            self.char_vectorizer.fit(corpus)
            self.feature_names.extend(self.char_vectorizer.get_feature_names_out().tolist())
        
        self.is_fitted = True
        return self

    def transform(self, texts: List[str]) -> np.ndarray:
        """Transform texts into L2-normalized TF-IDF vectors.

        Args:
            texts: List of text strings to transform.

        Returns:
            L2-normalized TF-IDF matrix (N, D) as numpy array.
        """
        if not self.is_fitted:
            raise ValueError("Embedder must be fitted before transforming")
        
        # Transform with word vectorizer
        word_vectors = self.word_vectorizer.transform(texts).toarray()
        
        # Transform with char vectorizer if enabled
        if self.char_vectorizer:
            char_vectors = self.char_vectorizer.transform(texts).toarray()
            vectors = np.hstack([word_vectors, char_vectors])
        else:
            vectors = word_vectors
        
        # L2-normalize the vectors
        return normalize(vectors, norm='l2', axis=1)

    def embed(self, text: str) -> Dict[str, Union[np.ndarray, List[Tuple[str, float]]]]:
        """Embed a single text into a vector with explainable top terms.

        Args:
            text: Input text string.

        Returns:
            Dict with:
                - vector: L2-normalized (1, D) numpy array (float32).
                - top_terms: List of (term, weight) tuples, up to 10.
        """
        if not self.is_fitted:
            raise ValueError("Embedder must be fitted before embedding")
        
        # Handle empty input
        if not text.strip():
            return {
                "vector": np.zeros((1, len(self.feature_names)), dtype=np.float32),
                "top_terms": []
            }
        
        # Transform text
        vector = self.transform([text])[0]
        
        # Get top terms (non-zero weights, sorted by weight)
        indices = np.argsort(vector)[::-1]
        top_terms = [
            (self.feature_names[i], float(vector[i]))
            for i in indices
            if vector[i] > 0
        ][:10]
        
        return {
            "vector": vector.reshape(1, -1),
            "top_terms": top_terms
        }

    def get_feature_names(self) -> List[str]:
        """Return the list of feature names (words and optionally char n-grams).

        Returns:
            List of feature names.
        """
        if not self.is_fitted:
            raise ValueError("Embedder must be fitted to get feature names")
        return self.feature_names

    def save(self, path: str) -> None:
        """Save the fitted embedder to a file.

        Args:
            path: File path to save the embedder.
        """
        if not self.is_fitted:
            raise ValueError("Embedder must be fitted before saving")
        joblib.dump({
            'word_vectorizer': self.word_vectorizer,
            'char_vectorizer': self.char_vectorizer,
            'feature_names': self.feature_names,
            'is_fitted': self.is_fitted,
            'stopwords': self.stopwords
        }, path)

    @staticmethod
    def load(path: str) -> 'TextEmbedder':
        """Load a fitted embedder from a file.

        Args:
            path: File path to load the embedder from.

        Returns:
            Loaded TextEmbedder instance.
        """
        data = joblib.load(path)
        embedder = TextEmbedder(stopwords=data['stopwords'])
        embedder.word_vectorizer = data['word_vectorizer']
        embedder.char_vectorizer = data['char_vectorizer']
        embedder.feature_names = data['feature_names']
        embedder.is_fitted = data['is_fitted']
        return embedder

if __name__ == "__main__":
    # Test TextEmbedder
    corpus = ["cat sat", "dog sat"]
    embedder = TextEmbedder(ngram_range=(1, 2), char_ngrams=False, max_features=100)
    embedder.fit(corpus)
    
    # Embed a single text
    result = embedder.embed("cat")
    print("Top terms:", result["top_terms"])
    print("Vector shape:", result["vector"].shape)