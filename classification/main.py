import os
import argparse
from train import train
from predict import load_model, predict_category, batch_predict


def main():
    parser = argparse.ArgumentParser(description='News Title Classification with BERT')
    parser.add_argument('--mode', type=str, default='train', choices=['train', 'predict'],
                        help='Mode: train or predict')
    parser.add_argument('--data_path', type=str, default='data/News Title.xls',
                        help='Path to the data file')
    parser.add_argument('--save_dir', type=str, default='models',
                        help='Directory to save the model')
    parser.add_argument('--model_path', type=str, default='models/bert_news_classifier_model.pt',
                        help='Path to the saved model')
    parser.add_argument('--tokenizer_info_path', type=str, default='models/bert_tokenizer_info.pkl',
                        help='Path to the tokenizer information')
    parser.add_argument('--bert_model', type=str, default='bert-base-uncased',
                        help='BERT model to use (e.g., bert-base-uncased)')
    parser.add_argument('--text', type=str, default='',
                        help='News title to classify')

    args = parser.parse_args()

    if args.mode == 'train':
        print('Training model with BERT...')
        model, tokenizer = train(
            args.data_path,
            args.save_dir,
            bert_model_name=args.bert_model
        )
    elif args.mode == 'predict':
        if not args.text:
            print('Please provide a news title to classify using --text')
            return

        print('Loading model...')
        model, tokenizer, max_length, categories_dict = load_model(args.model_path, args.tokenizer_info_path)

        print('Making prediction...')
        category = predict_category(model, args.text, tokenizer, categories_dict, max_length)
        print(f'The news title "{args.text}" is classified as: {category}')


def run_prediction(text, model_path='models/bert_news_classifier_model.pt',
                   tokenizer_info_path='models/bert_tokenizer_info.pkl'):
    """Run prediction on a single text without command line arguments"""
    print('Loading model...')
    model, tokenizer, max_length, categories_dict = load_model(model_path, tokenizer_info_path)

    print('Making prediction...')
    category = predict_category(model, text, tokenizer, categories_dict, max_length)
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
        model_path='models/bert_news_classifier_model.pt',
        tokenizer_info_path='models/bert_tokenizer_info.pkl'
    )

    # Option 3: Run multiple predictions
    # headlines = [
    #     "Senate passes new healthcare bill",
    #     "New smartphone features unveiled at tech conference",
    #     "Celebrity announces divorce after 10 years of marriage"
    # ]
    # for headline in headlines:
    #     run_prediction(headline)