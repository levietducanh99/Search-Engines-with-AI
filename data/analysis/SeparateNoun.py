# Cài đặt các thư viện cần thiết (nếu chưa có)
# pip install supabase
# pip install spacy

from supabase import create_client, Client
import spacy

# ------------------- Bước 1: Kết nối Supabase -------------------
# Thay YOUR_SUPABASE_URL và YOUR_SUPABASE_KEY bằng thông tin thật
url = "https://mlkqujqhrzvibontqatq.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1sa3F1anFocnp2aWJvbnRxYXRxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE2MjQzMDIsImV4cCI6MjA1NzIwMDMwMn0.-3X1fc9Xdo-2YSyR4lVkwxMV5N5-qc-cS3FMq63RVR0"
supabase: Client = create_client(url, key)

# Tên bảng bạn muốn làm việc
table_name = "WebScrapData"

# ------------------- Bước 2: Load mô hình NLP -------------------
nlp = spacy.load("en_core_web_sm")  # Nếu chưa có, chạy: python -m spacy download en_core_web_sm

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

        # ------------------- Bước 5: Cập nhật vào cột mới -------------------
        # Nếu bảng chưa có cột named_entities thì bạn phải tạo trước trên Supabase
        update_data = {
            "named_entities": named_entities  # Cột kiểu text[] hoặc JSON trên Supabase
        }
        supabase.table(table_name).update(update_data).eq("id", id).execute()

    print("✅ Đã tách và cập nhật xong tất cả tên riêng!")
else:
    print("⚠️ Không tìm thấy dữ liệu trong bảng.")

