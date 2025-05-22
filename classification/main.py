import os
import argparse
from train import train
from predict import load_model, predict_category, batch_predict


def main():
    parser = argparse.ArgumentParser(description='News Title Classification')
    parser.add_argument('--mode', type=str, default='train', choices=['train', 'predict'],
                        help='Mode: train or predict')
    parser.add_argument('--data_path', type=str, default='data/News Title.xls',
                        help='Path to the data file')
    parser.add_argument('--glove_path', type=str, default='embedding/glove',
                        help='Path to GloVe embeddings')
    parser.add_argument('--save_dir', type=str, default='models',
                        help='Directory to save the model')
    parser.add_argument('--model_path', type=str, default='models/news_classifier_model.pt',
                        help='Path to the saved model')
    parser.add_argument('--vocab_path', type=str, default='models/vocab_to_int.pkl',
                        help='Path to the saved vocabulary')
    parser.add_argument('--text', type=str, default='',
                        help='News title to classify')

    args = parser.parse_args()

    if args.mode == 'train':
        print('Training model...')
        model, vocab_to_int, _ = train(
            args.data_path,
            args.glove_path,
            args.save_dir
        )

        # Save vocabulary
        import pickle
        with open(os.path.join(args.save_dir, 'vocab_to_int.pkl'), 'wb') as f:
            pickle.dump(vocab_to_int, f)

    elif args.mode == 'predict':
        if not args.text:
            print('Please provide a news title to classify using --text')
            return

        print('Loading model...')
        model, vocab_to_int = load_model(args.model_path, args.vocab_path)

        print('Making prediction...')
        category = predict_category(model, args.text, vocab_to_int)
        print(f'The news title "{args.text}" is classified as: {category}')


if __name__ == '__main__':
    main()