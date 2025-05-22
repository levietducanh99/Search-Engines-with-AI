import torch
import torch.nn as nn
from transformers import BertModel, BertTokenizer

def load_bert_tokenizer(bert_model_name="bert-base-uncased"):
    """Load BERT tokenizer"""
    tokenizer = BertTokenizer.from_pretrained(bert_model_name)
    return tokenizer

def load_bert_model(bert_model_name="bert-base-uncased"):
    """Load pre-trained BERT model"""
    model = BertModel.from_pretrained(bert_model_name)
    return model

def create_bert_embeddings_layer(bert_model_name="bert-base-uncased", freeze_bert=True):
    """Create BERT embedding layer"""
    bert_model = load_bert_model(bert_model_name)
    
    # Freeze BERT parameters if specified
    if freeze_bert:
        for param in bert_model.parameters():
            param.requires_grad = False
    
    embedding_dim = bert_model.config.hidden_size  # 768 for base model
    
    return bert_model, embedding_dim
