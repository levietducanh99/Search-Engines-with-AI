import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_tfidf_vectorizer(texts, max_features=10000, ngram_range=(1, 2)):
    """
    Create and fit a TF-IDF vectorizer for text classification
    
    Args:
        texts: List of text documents
        max_features: Maximum number of features to extract
        ngram_range: Range of n-grams to consider
        
    Returns:
        Fitted TF-IDF vectorizer
    """
    logger.info(f"Creating TF-IDF vectorizer with {max_features} features and ngram_range={ngram_range}")
    
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        sublinear_tf=True,
        lowercase=True,
        stop_words='english'
    )
    
    # Fit the vectorizer on the texts
    vectorizer.fit(texts)
    logger.info(f"Vectorizer created with {len(vectorizer.get_feature_names_out())} features")
    
    return vectorizer

def save_vectorizer(vectorizer, save_path):
    """Save the vectorizer to disk"""
    with open(save_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    logger.info(f"Vectorizer saved to {save_path}")

def load_vectorizer(vectorizer_path):
    """Load the vectorizer from disk"""
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)
    logger.info(f"Vectorizer loaded with {len(vectorizer.get_feature_names_out())} features")
    return vectorizer
