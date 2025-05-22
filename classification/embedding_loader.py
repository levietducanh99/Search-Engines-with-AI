import bcolz
import pickle
import numpy as np
import torch
import torch.nn as nn
import os


def load_glove_vectors(glove_path, vector_size=300):
    """Load pre-trained GloVe word vectors"""
    vectors_path = f'{glove_path}/6B.{vector_size}.dat'
    words_path = f'{glove_path}/6B.{vector_size}_words.pkl'
    idx_path = f'{glove_path}/6B.{vector_size}_idx.pkl'

    # Check if processed files exist, otherwise create them
    if not (os.path.exists(vectors_path) and os.path.exists(words_path) and os.path.exists(idx_path)):
        # Process original GloVe file
        words = []
        idx = 0
        word2idx = {}
        vectors = bcolz.carray(np.zeros(1), rootdir=vectors_path, mode='w')

        with open(f'{glove_path}/glove.6B.{vector_size}d.txt', 'rb') as f:
            for l in f:
                line = l.decode().split()
                word = line[0]
                words.append(word)
                word2idx[word] = idx
                idx += 1
                vect = np.array(line[1:]).astype(np.float)
                vectors.append(vect)

        vectors = bcolz.carray(vectors[1:].reshape((400000, vector_size)), rootdir=vectors_path, mode='w')
        vectors.flush()
        pickle.dump(words, open(words_path, 'wb'))
        pickle.dump(word2idx, open(idx_path, 'wb'))

    # Load saved files
    vectors = bcolz.open(vectors_path)[:]
    words = pickle.load(open(words_path, 'rb'))
    word2idx = pickle.load(open(idx_path, 'rb'))

    # Create dictionary mapping words to vectors
    glove = {w: vectors[word2idx[w]] for w in words}

    return glove


def create_embedding_matrix(target_vocab, glove, emb_dim=300):
    """Create embedding matrix for vocabulary using pre-trained GloVe vectors"""
    matrix_len = len(target_vocab)
    weights_matrix = np.zeros((matrix_len, emb_dim))
    words_found = 0

    for i, word in enumerate(target_vocab):
        try:
            weights_matrix[i] = glove[word]
            words_found += 1
        except KeyError:
            weights_matrix[i] = np.random.normal(scale=0.6, size=(emb_dim,))

    print(f"Found {words_found}/{matrix_len} words in GloVe")
    return weights_matrix


def create_emb_layer(weights_matrix, non_trainable=False):
    """Create embedding layer from weights matrix"""
    num_embeddings, embedding_dim = weights_matrix.shape
    emb_layer = nn.Embedding(num_embeddings, embedding_dim)
    emb_layer.load_state_dict({'weight': torch.from_numpy(weights_matrix)})

    if non_trainable:
        emb_layer.weight.requires_grad = False

    return emb_layer, num_embeddings, embedding_dim