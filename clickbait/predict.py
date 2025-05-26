import joblib
import re
import pandas as pd
import argparse

# Define common clickbait/sensationalist words (same as in train.py)
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


def predict_from_file(model, filepath):
    """Predict multiple titles from a CSV file"""
    try:
        df = pd.read_csv(filepath)
        if 'title' not in df.columns:
            print("Error: CSV file must contain a 'title' column")
            return
        
        results = []
        for title in df['title']:
            result = predict_title(model, title)
            results.append({
                'title': title,
                'prediction': 'FAKE' if result['is_fake'] else 'REAL',
                'fake_probability': result['probability'],
                'clickbait_words': result['clickbait_words']
            })
        
        # Create results dataframe
        results_df = pd.DataFrame(results)
        print(f"Processed {len(results_df)} titles")
        return results_df
    
    except Exception as e:
        print(f"Error processing file: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Predict fake news from titles')
    parser.add_argument('--model', type=str, default='fake_news_detector.pkl',
                        help='Path to the trained model')
    parser.add_argument('--input', type=str, help='Path to CSV file with titles')
    parser.add_argument('--output', type=str, help='Path to save prediction results')
    parser.add_argument('--title', type=str, help='Single title to predict')
    
    args = parser.parse_args()
    
    # Load the model
    try:
        model = joblib.load(args.model)
        print(f"Model loaded from {args.model}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    # Process single title
    if args.title:
        result = predict_title(model, args.title)
        print(f"\nTitle: {args.title}")
        print(f"Prediction: {'FAKE' if result['is_fake'] else 'REAL'}")
        print(f"Fake probability: {result['probability']:.2f}")
        print(f"Clickbait words: {result['clickbait_words']}")
    
    # Process from file
    elif args.input:
        results_df = predict_from_file(model, args.input)
        if results_df is not None:
            if args.output:
                results_df.to_csv(args.output, index=False)
                print(f"Results saved to {args.output}")
            else:
                # Display first 10 results
                print("\nFirst 10 predictions:")
                print(results_df.head(10))
    
    # Interactive mode
    else:
        print("Enter titles to predict (type 'exit' to quit):")
        while True:
            title = input("\nTitle: ")
            if title.lower() == 'exit':
                break
            
            result = predict_title(model, title)
            print(f"Prediction: {'FAKE' if result['is_fake'] else 'REAL'}")
            print(f"Fake probability: {result['probability']:.2f}")
            print(f"Clickbait words: {result['clickbait_words']}")


if __name__ == "__main__":
    main()
