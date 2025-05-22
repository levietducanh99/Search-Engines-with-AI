import torch
import torch.nn as nn
import torch.utils.data
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from sklearn.model_selection import train_test_split
import os

from data_loader import load_data, clean_data, tokenize_titles, track_vocab
from data_loader import create_lookup_tables, encode_titles, pad_features
from embedding_loader import load_glove_vectors, create_embedding_matrix, create_emb_layer
from model import RNN


def train(data_path, glove_path, save_dir, batch_size=50, hidden_dim=256,
          seq_length=31, epochs=3, lr=0.0001, print_every=100):
    """Train the news classification model"""
    # Check for GPU
    train_on_gpu = torch.cuda.is_available()
    if train_on_gpu:
        print('Training on GPU')
    else:
        print('Training on CPU')

    # Load and clean data
    titles, labels = load_data(data_path)
    titles = clean_data(titles)

    # Tokenize and preprocess
    titles_token = tokenize_titles(titles)

    # Filter very long titles
    filtered_titles = []
    filtered_labels = []
    for title, label in zip(titles_token, labels):
        if len(title) < 100:
            filtered_titles.append(title)
            filtered_labels.append(label)

    titles_token = filtered_titles
    labels = np.array(filtered_labels)

    # Create vocabulary
    vocab_count = track_vocab(titles_token)
    vocab_to_int, int_to_vocab = create_lookup_tables(vocab_count)

    # Encode and pad titles
    title_ints = encode_titles(titles_token, vocab_to_int)
    features = pad_features(title_ints, seq_length)

    # Split dataset
    train_X, val_test_X, train_y, val_test_y = train_test_split(
        features, labels, test_size=0.2, random_state=42, shuffle=True, stratify=labels)

    val_X, test_X, val_y, test_y = train_test_split(
        val_test_X, val_test_y, test_size=0.5, random_state=42, shuffle=True, stratify=val_test_y)

    # Create Tensor datasets
    train_data = TensorDataset(torch.from_numpy(train_X), torch.from_numpy(train_y))
    valid_data = TensorDataset(torch.from_numpy(val_X), torch.from_numpy(val_y))
    test_data = TensorDataset(torch.from_numpy(test_X), torch.from_numpy(test_y))

    # DataLoaders
    num_workers = 0 if train_on_gpu else 0  # Adjust based on your system

    train_loader = DataLoader(train_data, shuffle=True, batch_size=batch_size, num_workers=num_workers)
    valid_loader = DataLoader(valid_data, shuffle=True, batch_size=batch_size, num_workers=num_workers)
    test_loader = DataLoader(test_data, shuffle=True, batch_size=batch_size, num_workers=num_workers)

    # Load GloVe embeddings
    glove = load_glove_vectors(glove_path)

    # Create embedding matrix
    sorted_vocab = sorted(vocab_count, key=vocab_count.get, reverse=True)
    weights_matrix = create_embedding_matrix(sorted_vocab, glove)

    # Create embedding layer
    embedding_layer = create_emb_layer(weights_matrix, True)

    # Initialize model
    net = RNN(embedding_layer, 4, hidden_dim, seq_length)

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, net.parameters()), lr=lr)

    # Move model to GPU if available
    if train_on_gpu:
        net.cuda()

    # Training parameters
    clip = 5  # gradient clipping

    # Training loop
    net.train()
    counter = 0
    for e in range(epochs):
        # Batch loop
        for inputs, labels in train_loader:
            counter += 1

            if train_on_gpu:
                inputs, labels = inputs.cuda(), labels.cuda()

            # Zero gradients
            net.zero_grad()

            # Forward pass
            output = net(inputs)

            # Calculate loss and backprop
            loss = criterion(output, labels)
            loss.backward()

            # Clip gradients
            nn.utils.clip_grad_norm_(net.parameters(), clip)

            # Update weights
            optimizer.step()

            # Print statistics
            if counter % print_every == 0:
                # Get validation loss
                val_losses = []
                net.eval()
                for val_inputs, val_labels in valid_loader:
                    if train_on_gpu:
                        val_inputs, val_labels = val_inputs.cuda(), val_labels.cuda()

                    val_output = net(val_inputs)
                    val_loss = criterion(val_output, val_labels)

                    val_losses.append(val_loss.item())

                net.train()
                print(f"Epoch: {e + 1}/{epochs}... "
                      f"Step: {counter}... "
                      f"Loss: {loss.item():.6f}... "
                      f"Val Loss: {np.mean(val_losses):.6f}")

    # Test the model
    test_model(net, test_loader, criterion, train_on_gpu)

    # Save the model
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_path = os.path.join(save_dir, 'news_classifier_model.pt')
    torch.save(net, save_path)
    print(f"Model saved to {save_path}")

    return net, vocab_to_int, int_to_vocab


def test_model(net, test_loader, criterion, train_on_gpu):
    """Test the trained model on test data"""
    test_losses = []
    num_correct = 0

    net.eval()
    # Iterate over test data
    for inputs, labels in test_loader:
        if train_on_gpu:
            inputs, labels = inputs.cuda(), labels.cuda()

        # Get predictions
        output = net(inputs)

        # Calculate loss
        test_loss = criterion(output, labels)
        test_losses.append(test_loss.item())

        # Get predictions
        pred = torch.argmax(output, dim=1)

        # Compare to true labels
        correct_tensor = pred.eq(labels)
        correct = np.squeeze(correct_tensor.cpu().numpy() if train_on_gpu else correct_tensor.numpy())
        num_correct += np.sum(correct)

    # Calculate test accuracy
    test_acc = num_correct / len(test_loader.dataset)

    # Print test results
    print(f"Test loss: {np.mean(test_losses):.3f}")
    print(f"Test accuracy: {test_acc:.3f}")

    return test_acc