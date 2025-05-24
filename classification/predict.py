import pickle
import logging
from data_loader import clean_shortforms, clean_symbol
from vectorizer import load_vectorizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_model(model_path, vectorizer_path, categories_dict_path):
    """
    Load the trained Naive Bayes model, vectorizer, and categories dictionary
    """
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    vectorizer = load_vectorizer(vectorizer_path)
    
    with open(categories_dict_path, 'rb') as f:
        categories_dict = pickle.load(f)
    
    return model, vectorizer, categories_dict

def predict_category(model, text, vectorizer, categories_dict=None):
    """
    Make a prediction for a single news title using Naive Bayes
    """
    # Clean and preprocess the text
    text = text.lower()
    text = clean_shortforms(text)
    text = clean_symbol(text)
    
    # Transform text to feature vector
    text_features = vectorizer.transform([text])
    
    # Make prediction
    pred = model.predict(text_features)[0]
    
    # Map prediction to category name
    if categories_dict is None:
        # Default categories if not provided
        categories = {0: 'Entertainment', 1: 'Business', 2: 'Technology', 3: 'Medical'}
    else:
        # Create reverse mapping from integer to category name
        categories = {v: k for k, v in categories_dict.items()}
    
    return categories[pred]

def batch_predict(model, texts, vectorizer, categories_dict=None):
    """
    Make predictions for multiple news titles using Naive Bayes
    """
    # Clean and preprocess the texts
    cleaned_texts = []
    for text in texts:
        text = text.lower()
        text = clean_shortforms(text)
        text = clean_symbol(text)
        cleaned_texts.append(text)
    
    # Transform texts to feature vectors
    text_features = vectorizer.transform(cleaned_texts)
    
    # Make predictions
    preds = model.predict(text_features)
    
    # Map predictions to category names
    if categories_dict is None:
        # Default categories if not provided
        categories = {0: 'Entertainment', 1: 'Business', 2: 'Technology', 3: 'Medical'}
    else:
        # Create reverse mapping from integer to category name
        categories = {v: k for k, v in categories_dict.items()}
    
    return [categories[pred] for pred in preds]
