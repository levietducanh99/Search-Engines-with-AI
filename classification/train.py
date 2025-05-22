import torch
import torch.nn as nn
import torch.utils.data
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from sklearn.model_selection import train_test_split
import os
import pickle

from data_loader import load_data, clean_data, encode_titles_for_bert, create_bert_dataset
from embedding_loader import load_bert_tokenizer, create_bert_embeddings_layer
from model import BERTClassifier


def train(data_path, save_dir, batch_size=32, hidden_dim=256,
          seq_length=64, epochs=3, lr=2e-5, print_every=100,
          bert_model_name="bert-base-uncased"):
    """Train the news classification model using BERT embeddings"""
    # Check for GPU
    train_on_gpu = torch.cuda.is_available()
    if train_on_gpu:
        print('Training on GPU')
    else:
        print('Training on CPU')

    # Load BERT tokenizer
    print("Loading BERT tokenizer...")
    tokenizer = load_bert_tokenizer(bert_model_name)

    # Load and clean data
    print("Loading and cleaning data...")
    titles, labels = load_data(data_path)
    titles = clean_data(titles)

    # Filter very long titles
    filtered_titles = []
    filtered_labels = []
    for title, label in zip(titles, labels):
        if len(title.split()) < 100:
            filtered_titles.append(title)
            filtered_labels.append(label)

    titles = pd.Series(filtered_titles)
    labels = np.array(filtered_labels)

    # Tokenize and encode data for BERT
    print("Encoding data for BERT...")
    input_ids, attention_masks = encode_titles_for_bert(titles, tokenizer, max_length=seq_length)

    # Split dataset
    train_inputs, val_test_inputs, train_masks, val_test_masks, train_labels, val_test_labels = train_test_split(
        input_ids, attention_masks, labels, 
        test_size=0.2, random_state=42, 
        stratify=labels
    )

    val_inputs, test_inputs, val_masks, test_masks, val_labels, test_labels = train_test_split(
        val_test_inputs, val_test_masks, val_test_labels,
        test_size=0.5, random_state=42,
        stratify=val_test_labels
    )

    # Create datasets
    train_data = create_bert_dataset(train_inputs, train_masks, train_labels)
    val_data = create_bert_dataset(val_inputs, val_masks, val_labels)
    test_data = create_bert_dataset(test_inputs, test_masks, test_labels)

    # Create DataLoaders
    train_loader = DataLoader(train_data, shuffle=True, batch_size=batch_size)
    valid_loader = DataLoader(val_data, shuffle=True, batch_size=batch_size)
    test_loader = DataLoader(test_data, shuffle=True, batch_size=batch_size)

    # Load BERT model for embeddings
    print("Loading BERT model...")
    bert_model, embedding_dim = create_bert_embeddings_layer(bert_model_name, freeze_bert=True)

    # Initialize model
    net = BERTClassifier(bert_model, 4, hidden_dim, seq_length)

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    # Use AdamW optimizer for BERT fine-tuning
    optimizer = torch.optim.AdamW(net.parameters(), lr=lr, eps=1e-8)

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
        for inputs, masks, labels in train_loader:
            counter += 1

            if train_on_gpu:
                inputs, masks, labels = inputs.cuda(), masks.cuda(), labels.cuda()

            # Zero gradients
            net.zero_grad()

            # Forward pass
            output = net(inputs, attention_mask=masks)

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
                for val_inputs, val_masks, val_labels in valid_loader:
                    if train_on_gpu:
                        val_inputs, val_masks, val_labels = val_inputs.cuda(), val_masks.cuda(), val_labels.cuda()

                    val_output = net(val_inputs, attention_mask=val_masks)
                    val_loss = criterion(val_output, val_labels)

                    val_losses.append(val_loss.item())

                net.train()
                print(f"Epoch: {e + 1}/{epochs}... "
                      f"Step: {counter}... "
                      f"Loss: {loss.item():.6f}... "
                      f"Val Loss: {np.mean(val_losses):.6f}")

    # Test the model
    test_model(net, test_loader, criterion, train_on_gpu)

    # Save the model and tokenizer
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_path = os.path.join(save_dir, 'bert_news_classifier_model.pt')
    torch.save(net, save_path)
    
    # Save tokenizer info
    tokenizer_info = {
        'bert_model_name': bert_model_name,
        'max_length': seq_length
    }
    with open(os.path.join(save_dir, 'bert_tokenizer_info.pkl'), 'wb') as f:
        pickle.dump(tokenizer_info, f)
        
    print(f"Model saved to {save_path}")

    return net, tokenizer


def test_model(net, test_loader, criterion, train_on_gpu):
    """Test the trained model on test data"""
    test_losses = []
    num_correct = 0

    net.eval()
    # Iterate over test data
    for inputs, masks, labels in test_loader:
        if train_on_gpu:
            inputs, masks, labels = inputs.cuda(), masks.cuda(), labels.cuda()

        # Get predictions
        output = net(inputs, attention_mask=masks)

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
