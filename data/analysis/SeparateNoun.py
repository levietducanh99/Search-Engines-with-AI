from supabase import create_client, Client
import spacy

# ------------------- Bước 1: Kết nối Supabase -------------------
url = "https://mlkqujqhrzvibontqatq.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1sa3F1anFocnp2aWJvbnRxYXRxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MTYyNDMwMiwiZXhwIjoyMDU3MjAwMzAyfQ.9GKUKNB2qqFiH6pn_f6NBZqdJsuVHtNjUNhQZy5IEBE"
supabase: Client = create_client(url, key)

table_name = "WebScrapData"

# ------------------- Bước 2: Load mô hình NLP -------------------
nlp = spacy.load("en_core_web_trf")  # Nếu chưa có, chạy: python -m spacy download en_core_web_sm

# Hàm tách tên riêng
def extract_named_entities(text):
    doc = nlp(text)
    entities = [ent.text for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "GPE", "PRODUCT"]]
    return entities

# ------------------- Bước 3: Lấy dữ liệu titles -------------------
response = supabase.table(table_name).select("id, headline").execute()

if response.data:
    for item in response.data:
        id = item['id']
        title = item['headline']

        # ------------------- Bước 4: Tách tên riêng -------------------
        named_entities = extract_named_entities(title)

        # ------------------- Bước 5: Cập nhật vào Supabase -------------------
        update_data = {
            "keywords_proper_nouns": named_entities
        }

        update_response = supabase.table(table_name).update(update_data).eq("id", id).execute()


    print("✅ Đã tách và cập nhật xong !")
else:
    print("⚠️ Không tìm thấy dữ liệu trong bảng.")

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