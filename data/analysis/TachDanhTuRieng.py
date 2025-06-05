import psycopg2
import spacy
import time

# ------------------- Bước 1: Kết nối PostgreSQL -------------------
conn = psycopg2.connect(
    host="dpg-d0g2d1idbo4c73auv9i0-a.singapore-postgres.render.com",
    port="5432",
    user="hybrid_search_database_user",
    password="EvaQhGOaGF7QgdgteoxWvmfKvWe0VqM1",
    dbname="hybrid_search_database"
)
cursor = conn.cursor()

# ------------------- Bước 2: Load mô hình NLP -------------------
nlp = spacy.load("en_core_web_trf")

# ------------------- Bước 3: Xử lý batch -------------------
BATCH_SIZE = 1000

def get_batch_without_proper_nouns():
    query = f"""
        SELECT id, headline, short_description
        FROM "WebScrapData_rows"
        WHERE keywords_proper_nouns IS NULL
        LIMIT {BATCH_SIZE};
    """
    cursor.execute(query)
    return cursor.fetchall()

def update_keywords_proper_nouns(data):
    updated_count = 0

    for id_, headline, short_description in data:
        text = headline or short_description or ""
        doc = nlp(text)

        proper_nouns = [ent.text for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "GPE", "PRODUCT"]]

        if not proper_nouns and short_description:
            doc = nlp(short_description)
            proper_nouns = [ent.text for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "GPE", "PRODUCT"]]

        if not proper_nouns:
            continue  # Không cập nhật nếu không có tên riêng

        keywords_str = ", ".join(proper_nouns)
        update_query = """
            UPDATE "WebScrapData_rows"
            SET keywords_proper_nouns = %s
            WHERE id = %s;
        """
        cursor.execute(update_query, (keywords_str, id_))
        updated_count += 1

    conn.commit()
    print(f"✅ Đã thực sự cập nhật {updated_count} dòng.")

# ------------------- Bước 4: Lặp cho tới khi hết -------------------
while True:
    batch = get_batch_without_proper_nouns()
    if not batch:
        print("✅ Tất cả dòng đã được xử lý.")
        break
    update_keywords_proper_nouns(batch)
    time.sleep(1)