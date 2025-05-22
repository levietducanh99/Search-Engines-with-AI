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
        model, tokenizer, max_length = load_model(args.model_path, args.tokenizer_info_path)

        print('Making prediction...')
        category = predict_category(model, args.text, tokenizer, max_length)
        print(f'The news title "{args.text}" is classified as: {category}')


if __name__ == '__main__':
    main()
