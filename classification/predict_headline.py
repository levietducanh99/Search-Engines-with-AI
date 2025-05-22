# create this as predict_headline.py
from predict import load_model, predict_category


def predict_headline(headline, model_path='models/bert_news_classifier_model.pt',
                     tokenizer_info_path='models/bert_tokenizer_info.pkl'):
    """Simple function to predict the category of a news headline"""
    model, tokenizer, max_length, categories_dict = load_model(model_path, tokenizer_info_path)
    category = predict_category(model, headline, tokenizer, categories_dict, max_length)
    return category


if __name__ == "__main__":
    # You can modify this headline directly in the code
    headline = "Senate passes new healthcare bill"

    category = predict_headline(headline)
    print(f'The news headline "{headline}" is classified as: {category}')

    # Interactive mode - uncomment to use
    # while True:
    #     headline = input("\nEnter a news headline (or 'quit' to exit): ")
    #     if headline.lower() == 'quit':
    #         break
    #     category = predict_headline(headline)
    #     print(f'Predicted category: {category}')