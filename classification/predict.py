import torch
import numpy as np
import pickle
from transformers import BertTokenizer
from data_loader import clean_shortforms, clean_symbol


def load_model(model_path, tokenizer_info_path):
    """Load the trained BERT model and tokenizer info"""
    model = torch.load(model_path)
    
    # Load tokenizer info
    with open(tokenizer_info_path, 'rb') as f:
        tokenizer_info = pickle.load(f)
    
    # Load the tokenizer with the same configuration used for training
    tokenizer = BertTokenizer.from_pretrained(tokenizer_info['bert_model_name'])
    max_length = tokenizer_info['max_length']
    
    return model, tokenizer, max_length


def predict_category(model, text, tokenizer, max_length=64):
    """Make a prediction for a single news title using BERT"""
    # Clean and preprocess the text
    text = text.lower()
    text = clean_shortforms(text)
    text = clean_symbol(text)

    # Tokenize with BERT tokenizer
    encoded_text = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        return_attention_mask=True,
        padding='max_length',
        max_length=max_length,
        truncation=True,
        return_tensors='pt'
    )
    
    input_ids = encoded_text['input_ids']
    attention_mask = encoded_text['attention_mask']

    # Set model to evaluation mode
    model.eval()

    # Make prediction
    with torch.no_grad():
        output = model(input_ids, attention_mask=attention_mask)

    # Get predicted category
    pred = torch.argmax(output, dim=1).item()

    # Map prediction to category name
    categories = {0: 'Entertainment', 1: 'Business', 2: 'Technology', 3: 'Medical'}
    return categories[pred]


def batch_predict(model, texts, tokenizer, max_length=64):
    """Make predictions for multiple news titles using BERT"""
    predictions = []
    for text in texts:
        category = predict_category(model, text, tokenizer, max_length)
        predictions.append(category)
    return predictions
