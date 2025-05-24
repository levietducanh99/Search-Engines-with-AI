import os
import argparse
from train import train
from predict import load_model, predict_category, batch_predict

def main():
    parser = argparse.ArgumentParser(description='News Title Classification with Naive Bayes')
    parser.add_argument('--mode', type=str, default='train', choices=['train', 'predict'],
                        help='Mode: train or predict')
    parser.add_argument('--data_path', type=str, default='data/News Title.xls',
                        help='Path to the data file')
    parser.add_argument('--save_dir', type=str, default='models',
                        help='Directory to save the model')
    parser.add_argument('--model_path', type=str, default='models/naive_bayes_news_classifier.pkl',
                        help='Path to the saved model')
    parser.add_argument('--vectorizer_path', type=str, default='models/tfidf_vectorizer.pkl',
                        help='Path to the saved vectorizer')
    parser.add_argument('--categories_dict_path', type=str, default='models/categories_dict.pkl',
                        help='Path to the categories dictionary')
    parser.add_argument('--text', type=str, default='',
                        help='News title to classify')

    args = parser.parse_args()

    if args.mode == 'train':
        print('Training Naive Bayes model...')
        model, vectorizer, categories_dict = train(
            args.data_path,
            args.save_dir
        )
    elif args.mode == 'predict':
        if not args.text:
            print('Please provide a news title to classify using --text')
            return

        print('Loading model...')
        model, vectorizer, categories_dict = load_model(
            args.model_path, 
            args.vectorizer_path,
            args.categories_dict_path
        )

        print('Making prediction...')
        category = predict_category(model, args.text, vectorizer, categories_dict)
        print(f'The news title "{args.text}" is classified as: {category}')

def run_prediction(text, model_path='models/naive_bayes_news_classifier.pkl',
                  vectorizer_path='models/tfidf_vectorizer.pkl',
                  categories_dict_path='models/categories_dict.pkl'):
    """Run prediction on a single text without command line arguments"""
    print('Loading model...')
    model, vectorizer, categories_dict = load_model(model_path, vectorizer_path, categories_dict_path)

    print('Making prediction...')
    category = predict_category(model, text, vectorizer, categories_dict)
    print(f'The news title "{text}" is classified as: {category}')
    return category

if __name__ == '__main__':
    # You can choose to use command line arguments or run directly
    # Uncomment the option you want to use

    # Option 1: Use command line arguments
    # main()

    # Option 2: Run prediction directly
    text_to_predict = "Senate passes new healthcare bill"
    run_prediction(
        text=text_to_predict,
        model_path='models/naive_bayes_news_classifier.pkl',
        vectorizer_path='models/tfidf_vectorizer.pkl',
        categories_dict_path='models/categories_dict.pkl'
    )

    # Option 3: Run multiple predictions
    # headlines = [
    #     "Senate passes new healthcare bill",
    #     "New smartphone features unveiled at tech conference",
    #     "Celebrity announces divorce after 10 years of marriage"
    # ]
    # for headline in headlines:
    #     run_prediction(headline)
