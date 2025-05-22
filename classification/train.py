import torch
import torch.nn as nn
import torch.utils.data
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import pandas as pd
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
    titles, labels, categories_dict = load_data(data_path)
    titles = clean_data(titles)

    # Get number of output classes
    num_classes = len(categories_dict)
    print(f"Training model with {num_classes} categories")

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

    # Initialize model with the correct number of output classes
    net = BERTClassifier(bert_model, num_classes, hidden_dim, seq_length)

    if train_on_gpu:
        net.cuda()

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=lr)

    # Training
    counter = 0
    net.train()
    for e in range(epochs):
        train_losses = []

        for inputs, masks, labels in train_loader:
            counter += 1

            if train_on_gpu:
                inputs, masks, labels = inputs.cuda(), masks.cuda(), labels.cuda()

            # Zero gradients
            net.zero_grad()

            # Forward pass
            output = net(inputs, attention_mask=masks)

            # Calculate loss
            loss = criterion(output, labels)
            train_losses.append(loss.item())

            # Backward pass
            loss.backward()

            # Update weights
            optimizer.step()

            # Print training status
            if counter % print_every == 0:
                net.eval()

                # Validation pass
                val_losses = []
                val_correct = 0
                for val_inputs, val_masks, val_labels in valid_loader:
                    if train_on_gpu:
                        val_inputs, val_masks, val_labels = val_inputs.cuda(), val_masks.cuda(), val_labels.cuda()

                    val_output = net(val_inputs, attention_mask=val_masks)
                    val_loss = criterion(val_output, val_labels)
                    val_losses.append(val_loss.item())

                    # Calculate accuracy
                    val_pred = torch.argmax(val_output, dim=1)
                    val_correct += torch.sum(val_pred == val_labels).item()

                val_acc = val_correct / len(valid_loader.dataset)

                net.train()
                print(f"Epoch: {e + 1}/{epochs}...")
                print(f"Step: {counter}...")
                print(f"Loss: {np.mean(train_losses):.4f}...")
                print(f"Val Loss: {np.mean(val_losses):.4f}")
                print(f"Val Accuracy: {val_acc:.4f}")

    # Test the final model
    test_acc = test_model(net, test_loader, criterion, train_on_gpu)

    # Save the model, tokenizer info, and categories dictionary
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_path = os.path.join(save_dir, 'bert_news_classifier_model.pt')
    torch.save(net, save_path)

    # Save tokenizer info and categories
    tokenizer_info = {
        'bert_model_name': bert_model_name,
        'max_length': seq_length,
        'categories_dict': categories_dict
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


if __name__ == "__main__":
    # This allows you to run training directly by running this file
    data_path = "G:\\AI\\Search-Engines-with-AI\\classification\\category.csv"
    save_dir = "models"

    # You can adjust these parameters as needed
    train(
        data_path=data_path,
        save_dir=save_dir,
        batch_size=16,  # Smaller batch size if memory is an issue
        hidden_dim=256,
        seq_length=64,
        epochs=3,
        lr=2e-5,
        print_every=50,
        bert_model_name="bert-base-uncased"
    )