    from supabase import create_client
    from dotenv import load_dotenv
    import os
    import time
    from tabulate import tabulate
    import spacy
    import nltk
    from nltk.corpus import wordnet

    # ------------------- Bước 1: Kết nối Supabase -------------------
    load_dotenv(os.path.join(os.path.dirname(_file_), "../../.env"))
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)


    def new_supabase():
        return create_client(url, key)


    table_name = "WebScrapData"

    # ------------------- Bước 2: Load mô hình NLP -------------------
    nlp = spacy.load("en_core_web_trf")  # Nếu chưa có, chạy: python -m spacy download en_core_web_sm


    # Hàm tách tên riêng
    def extract_named_entities(text):
        doc = nlp(text)
        entities = [ent.text for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "GPE", "PRODUCT"]]
        return entities


    # ------------------- Bước 3: Lấy dữ liệu titles -------------------
    def get_headlines_without_proper_nouns():
        while True:
            responses = supabase.rpc("get_headlines_without_keywords_proper_nouns").execute()
            if (not responses.data):
                print("No headlines found without keywords.")
                break

            keywords_proper_nouns_update = []

            for response in responses.data:
                headline = response["headline"]
                short_description = response["short_description"]
                doc = nlp(headline)

                # ------------------- Bước 4: Tách tên riêng -------------------
                keywords_proper_nouns = [ent.text.lower() for ent in doc.ents if
                                         ent.label_ in ["PERSON", "ORG", "GPE", "PRODUCT"]]

                if (not keywords_proper_nouns):
                    doc = nlp(short_description)
                    keywords_proper_nouns = [ent.text.lower() for ent in doc.ents if
                                             ent.label_ in ["PERSON", "ORG", "GPE", "PRODUCT"]]

                keywords_proper_nouns_update.append({
                    "id": response["id"],
                    "keywords_proper_nouns": " ".join(keywords_proper_nouns)
                })

            # ------------------- Bước 5: Cập nhật vào Supabase -------------------
            if keywords_proper_nouns_update:
                supabase.table("WebScrapData").upsert(keywords_proper_nouns_update).execute()

            print("Another 1000 headlines processed, renewing connection...")
            time.sleep(1)
            new_supabase()


    if _name_ == "_main_":
        get_headlines_without_proper_nouns()