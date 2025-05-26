import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import re
import joblib
from nltk.corpus import stopwords
import nltk

# Download necessary NLTK data
nltk.download('stopwords')

# Define common clickbait/sensationalist words
CLICKBAIT_WORDS = ['shocking', 'wow', 'unbelievable', 'amazing',
                   'you won\'t believe', 'mind-blowing', 'outrageous',
                   'secret', 'never seen before', 'warning', 'urgent',
                   'conspiracy', 'exposed', 'miracle', 'this is why',
                   'banned', 'controversial', 'breaking']


def preprocess_text(text):
    """Clean and normalize text data"""
    if not isinstance(text, str):
        return ""

    # Convert to lowercase
    text = text.lower()
    # Remove special characters and extra whitespace
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def add_clickbait_features(df):
    """Add features based on presence of clickbait words"""
    # Initialize features
    for word in CLICKBAIT_WORDS:
        col_name = f'has_{word.replace(" ", "_")}'
        df[col_name] = df['clean_title'].str.contains(word, case=False).astype(int)

    # Total clickbait word count
    df['clickbait_word_count'] = df[[f'has_{word.replace(" ", "_")}'
                                     for word in CLICKBAIT_WORDS]].sum(axis=1)
    return df


def load_and_prepare_data():
    """Load and prepare data from CSV files"""
    # Load datasets
    fake_df = pd.read_csv('fake.csv')
    true_df = pd.read_csv('true.csv')

    # Add labels (1 for fake, 0 for true)
    fake_df['label'] = 1
    true_df['label'] = 0

    # Combine datasets
    df = pd.concat([fake_df, true_df], axis=0).reset_index(drop=True)

    # Clean titles
    df['clean_title'] = df['title'].apply(preprocess_text)

    # Add clickbait features
    df = add_clickbait_features(df)

    return df


def train_model():
    """Train and evaluate the fake news detection model"""
    # Load and prepare data
    df = load_and_prepare_data()

    # Prepare features and target
    X = df['clean_title']  # Using only the title text
    y = df['label']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Create model pipeline
    model = Pipeline([
        ('tfidf', TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )),
        ('classifier', RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            class_weight='balanced',
            random_state=42
        ))
    ])

    # Train the model
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))

    # Plot confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.show()

    # Save the model
    joblib.dump(model, 'fake_news_detector.pkl')

    return model


def predict_title(model, title):
    """Predict if a title is fake news"""
    # Clean the title
    clean_title = preprocess_text(title)

    # Make prediction
    prediction = model.predict([clean_title])[0]
    probability = model.predict_proba([clean_title])[0][1]

    # Find clickbait words
    clickbait_words_found = [word for word in CLICKBAIT_WORDS
                             if word in clean_title.lower()]

    return {
        'is_fake': bool(prediction),
        'probability': probability,
        'clickbait_words': clickbait_words_found
    }


if __name__ == "__main__":
    model = train_model()

    # Test some examples
    example_titles = [
        "Scientists discover new cancer treatment",
        "SHOCKING: You won't believe what this politician did!",
        "New economic policy announced by government",
        "EXPOSED: The secret conspiracy they don't want you to know"
    ]

    for title in example_titles:
        result = predict_title(model, title)
        print(f"\nTitle: {title}")
        print(f"Prediction: {'FAKE' if result['is_fake'] else 'REAL'}")
        print(f"Fake probability: {result['probability']:.2f}")
        print(f"Clickbait words: {result['clickbait_words']}")