import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
import logging

from data_loader import load_data, clean_data
from vectorizer import create_tfidf_vectorizer, save_vectorizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def train(data_path, save_dir, max_features=10000, ngram_range=(1, 2), alpha=1.0):
    """
    Train a Naive Bayes model for news classification
    
    Args:
        data_path: Path to the data file
        save_dir: Directory to save the model
        max_features: Maximum number of features for TF-IDF
        ngram_range: Range of n-grams to consider
        alpha: Smoothing parameter for Naive Bayes
        
    Returns:
        The trained model and vectorizer
    """
    # Load and clean data
    logger.info("Loading and cleaning data...")
    titles, labels, categories_dict = load_data(data_path)
    titles = clean_data(titles)
    
    # Get number of output classes
    num_classes = len(categories_dict)
    logger.info(f"Training model with {num_classes} categories")
    
    # Split the dataset
    train_titles, test_titles, train_labels, test_labels = train_test_split(
        titles, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    logger.info(f"Train set size: {len(train_titles)}, Test set size: {len(test_titles)}")
    
    # Create TF-IDF vectorizer
    vectorizer = create_tfidf_vectorizer(train_titles, max_features=max_features, ngram_range=ngram_range)
    
    # Transform texts to feature vectors
    logger.info("Transforming texts to TF-IDF feature vectors...")
    X_train = vectorizer.transform(train_titles)
    X_test = vectorizer.transform(test_titles)
    
    # Train Naive Bayes model
    logger.info(f"Training Multinomial Naive Bayes model with alpha={alpha}...")
    model = MultinomialNB(alpha=alpha)
    model.fit(X_train, train_labels)
    
    # Evaluate the model
    train_pred = model.predict(X_train)
    train_accuracy = accuracy_score(train_labels, train_pred)
    logger.info(f"Training accuracy: {train_accuracy:.4f}")
    
    test_pred = model.predict(X_test)
    test_accuracy = accuracy_score(test_labels, test_pred)
    logger.info(f"Test accuracy: {test_accuracy:.4f}")
    
    # Print detailed classification report
    logger.info("Classification report on test data:")
    logger.info("\n" + classification_report(test_labels, test_pred))
    
    # Save the model and vectorizer
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    model_path = os.path.join(save_dir, 'naive_bayes_news_classifier.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    logger.info(f"Model saved to {model_path}")
    
    vectorizer_path = os.path.join(save_dir, 'tfidf_vectorizer.pkl')
    save_vectorizer(vectorizer, vectorizer_path)
    
    # Save categories dictionary
    categories_dict_path = os.path.join(save_dir, 'categories_dict.pkl')
    with open(categories_dict_path, 'wb') as f:
        pickle.dump(categories_dict, f)
    logger.info(f"Categories dictionary saved to {categories_dict_path}")
    
    return model, vectorizer, categories_dict

if __name__ == "__main__":
    # This allows you to run training directly by running this file
    data_path = "./category.csv"
    save_dir = "models"
    
    train(
        data_path=data_path,
        save_dir=save_dir,
        max_features=10000,
        ngram_range=(1, 2),
        alpha=0.1  # Lower alpha often works better for text classification
    )
