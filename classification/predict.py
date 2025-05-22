import torch
import numpy as np
import pickle
from data_loader import clean_shortforms, clean_symbol


def load_model(model_path, vocab_path):
    """Load the trained model and vocabulary"""
    model = torch.load(model_path)
    vocab_to_int = pickle.load(open(vocab_path, 'rb'))

    return model, vocab_to_int


def predict_category(model, text, vocab_to_int, seq_length=31):
    """Make a prediction for a single news title"""
    # Clean and preprocess the text
    text = text.lower()
    text = clean_shortforms(text)
    text = clean_symbol(text)

    # Tokenize
    words = text.split()

    # Convert to integers
    word_ints = []
    for word in words:
        if word in vocab_to_int:
            word_ints.append(vocab_to_int[word])
        else:
            # Handle unknown words (could use a special token or skip)
            pass

    # Pad
    features = np.zeros(seq_length, dtype=int)
    features[-len(word_ints):] = np.array(word_ints)[:seq_length]

    # Convert to tensor
    features_tensor = torch.from_numpy(features).unsqueeze(0)  # Add batch dimension

    # Set model to evaluation mode
    model.eval()

    # Make prediction
    with torch.no_grad():
        output = model(features_tensor)

    # Get predicted category
    pred = torch.argmax(output, dim=1).item()

    # Map prediction to category name
    categories = {0: 'Entertainment', 1: 'Business', 2: 'Technology', 3: 'Medical'}
    return categories[pred]


def batch_predict(model, texts, vocab_to_int, seq_length=31):
    """Make predictions for multiple news titles"""
    predictions = []
    for text in texts:
        category = predict_category(model, text, vocab_to_int, seq_length)
        predictions.append(category)
    return predictions