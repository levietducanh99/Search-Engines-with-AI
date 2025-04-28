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