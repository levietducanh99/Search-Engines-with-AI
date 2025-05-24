from predict import load_model, predict_category

def predict_headline(headline, 
                    model_path='models/naive_bayes_news_classifier.pkl',
                    vectorizer_path='models/tfidf_vectorizer.pkl',
                    categories_dict_path='models/categories_dict.pkl'):
    """Simple function to predict the category of a news headline using Naive Bayes"""
    model, vectorizer, categories_dict = load_model(model_path, vectorizer_path, categories_dict_path)
    category = predict_category(model, headline, vectorizer, categories_dict)
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
