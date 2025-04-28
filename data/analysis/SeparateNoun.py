from supabase import create_client, Client
import spacy

# ------------------- Bước 1: Kết nối Supabase -------------------
url = "https://mlkqujqhrzvibontqatq.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1sa3F1anFocnp2aWJvbnRxYXRxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE2MjQzMDIsImV4cCI6MjA1NzIwMDMwMn0.-3X1fc9Xdo-2YSyR4lVkwxMV5N5-qc-cS3FMq63RVR0"
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
response = supabase.table(table_name).select("id, headline").limit(20).execute()

if response.data:
    for item in response.data:
        id = item['id']
        title = item['headline']

        # ------------------- Bước 4: Tách tên riêng -------------------
        named_entities = extract_named_entities(title)

        print(f"ID: {id} | Title: {title}")
        print(f"Named Entities: {named_entities}")
        print("-" * 40)

    else:
        print("⚠️ Không tìm thấy dữ liệu trong bảng.")