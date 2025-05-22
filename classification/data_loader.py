import pandas as pd
import numpy as np
import re
import torch


def load_data(file_path):
    """Load news title data from Excel file"""
    df = pd.read_excel(file_path)
    titles = df['News Title']
    labels = df['Category']

    # Transform labels to integers
    dict_labels = {'Entertainment': 0, 'Business': 1, 'Technology': 2, 'Medical': 3}
    labels = pd.Series(labels).replace(dict_labels)

    return titles, labels.values


def clean_data(titles):
    """Clean the news title data"""
    # Lowercase all words
    titles = titles.apply(lambda x: x.lower())

    # Remove short forms
    titles = titles.apply(lambda x: clean_shortforms(x))

    # Remove symbols and punctuations
    titles = titles.apply(lambda x: clean_symbol(x))

    return titles


def clean_shortforms(text):
    """Replace short forms with their complete forms"""
    # Dictionary of short form words and misspellings
    short_forms_dict = {
        "ain't": "is not", "aren't": "are not", "can't": "cannot",
        "'cause": "because", "could've": "could have", "couldn't": "could not",
        "didn't": "did not", "doesn't": "does not", "don't": "do not", "hadn't": "had not",
        "hasn't": "has not", "haven't": "have not", "he'd": "he would", "he'll": "he will",
        "he's": "he is", "how'd": "how did", "how'd'y": "how do you", "how'll": "how will",
        "how's": "how is", "I'd": "I would", "I'd've": "I would have", "I'll": "I will",
        "I'll've": "I will have", "I'm": "I am", "I've": "I have", "i'd": "i would",
        "i'd've": "i would have", "i'll": "i will", "i'll've": "i will have", "i'm": "i am",
        "i've": "i have", "isn't": "is not", "it'd": "it would", "it'd've": "it would have",
        "it'll": "it will", "it'll've": "it will have", "it's": "it is", "let's": "let us",
        "ma'am": "madam", "mayn't": "may not", "might've": "might have", "mightn't": "might not",
        "mightn't've": "might not have", "must've": "must have", "mustn't": "must not",
        "mustn't've": "must not have", "needn't": "need not", "needn't've": "need not have",
        "o'clock": "of the clock", "oughtn't": "ought not", "oughtn't've": "ought not have",
        "shan't": "shall not", "sha'n't": "shall not", "shan't've": "shall not have",
        "she'd": "she would", "she'd've": "she would have", "she'll": "she will",
        "she'll've": "she will have", "she's": "she is", "should've": "should have",
        "shouldn't": "should not", "shouldn't've": "should not have", "so've": "so have",
        "so's": "so as", "this's": "this is", "that'd": "that would", "that'd've": "that would have",
        "that's": "that is", "there'd": "there would", "there'd've": "there would have",
        "there's": "there is", "here's": "here is", "they'd": "they would",
        "they'd've": "they would have", "they'll": "they will", "they'll've": "they will have",
        "they're": "they are", "they've": "they have", "to've": "to have", "wasn't": "was not",
        "we'd": "we would", "we'd've": "we would have", "we'll": "we will",
        "we'll've": "we will have", "we're": "we are", "we've": "we have",
        "weren't": "were not", "what'll": "what will", "what'll've": "what will have",
        "what're": "what are", "what's": "what is", "what've": "what have",
        "when's": "when is", "when've": "when have", "where'd": "where did",
        "where's": "where is", "where've": "where have", "who'll": "who will",
        "who'll've": "who will have", "who's": "who is", "who've": "who have", "why's": "why is",
        "why've": "why have", "will've": "will have", "won't": "will not", "won't've": "will not have",
        "would've": "would have", "wouldn't": "would not", "wouldn't've": "would not have",
        "y'all": "you all", "y'all'd": "you all would", "y'all'd've": "you all would have",
        "y'all're": "you all are", "y'all've": "you all have", "you'd": "you would",
        "you'd've": "you would have", "you'll": "you will", "you'll've": "you will have",
        "you're": "you are", "you've": "you have"
    }

    clean_text = text
    for shortform in short_forms_dict.keys():
        if re.search(shortform, text):
            clean_text = re.sub(shortform, short_forms_dict[shortform], text)
    return clean_text


def clean_symbol(text):
    """Remove all symbols from the text"""
    symbols = [',', '.', '"', ':', ')', '(', '-', '!', '?', '|',
               ';', "'", '$', '&', '/', '[', ']', '>', '%', '=',
               '#', '*', '+', '\\', '•', '~', '@', '£', '·', '_',
               '{', '}', '©', '^', '®', '`', '<', '→', '°', '€',
               '™', '›', '♥', '←', '×', '§', '″', '′', 'Â', '█',
               '½', 'à', '…', '"', '★', '"', '–', '●', 'â', '►',
               '−', '¢', '²', '¬', '░', '¶', '↑', '±', '¿', '▾',
               '═', '¦', '║', '―', '¥', '▓', '—', '‹', '─', '▒', '：',
               '¼', '⊕', '▼', '▪', '†', '■', ''', '▀', '¨', '▄', '♫', 
              '☆', 'é', '¯', '♦', '¤', '▲', 'è', '¸', '¾', 'Ã', '⋅', 
              ''', '∞', '∙', '）', '↓', '、', '│', '（', '»', '，', '♪',
               '╩', '╚', '³', '・', '╦', '╣', '╔', '╗', '▬', '❤', 'ï', 'Ø', '¹', '≤', '‡', '√']

    text = str(text)
    for symbol in symbols:
        text = text.replace(symbol, '')
    return text


def tokenize_titles(titles):
    """Tokenize titles by splitting on spaces"""
    return titles.apply(lambda x: x.split())


def track_vocab(sentences):
    """Count occurrences of words in all sentences"""
    vocab = {}
    for sentence in sentences:
        for word in sentence:
            try:
                vocab[word] += 1
            except KeyError:
                vocab[word] = 1
    return vocab


def create_lookup_tables(vocab_count):
    """Create lookup tables for vocabulary"""
    # Sort words by frequency
    sorted_vocab = sorted(vocab_count, key=vocab_count.get, reverse=True)

    # Create dictionaries
    int_to_vocab = {ii: word for ii, word in enumerate(sorted_vocab)}
    vocab_to_int = {word: ii for ii, word in int_to_vocab.items()}

    return vocab_to_int, int_to_vocab


def encode_titles(titles_token, vocab_to_int):
    """Encode tokenized titles to integers"""
    title_ints = []
    for title in titles_token:
        title_ints.append([vocab_to_int[word] for word in title])
    return title_ints


def pad_features(sentences_token, seq_length):
    """Pad titles to a specific length"""
    features = np.zeros((len(sentences_token), seq_length), dtype=int)

    for i, row in enumerate(sentences_token):
        features[i, -len(row):] = np.array(row)[:seq_length]

    return features


def encode_titles_for_bert(titles, tokenizer, max_length=64):
    """
    Tokenize and encode titles for BERT processing
    Returns input_ids and attention_masks
    """
    # Tokenize all titles
    encoded_data = tokenizer.batch_encode_plus(
        titles.tolist(),
        add_special_tokens=True,
        return_attention_mask=True,
        padding='max_length',
        max_length=max_length,
        truncation=True,
        return_tensors='pt'
    )
    
    input_ids = encoded_data['input_ids']
    attention_masks = encoded_data['attention_mask']
    
    return input_ids, attention_masks


def create_bert_dataset(input_ids, attention_masks, labels):
    """Create TensorDataset for BERT inputs"""
    return torch.utils.data.TensorDataset(
        input_ids,
        attention_masks,
        torch.tensor(labels)
    )
