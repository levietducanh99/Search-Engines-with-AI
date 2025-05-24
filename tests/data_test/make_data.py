import pandas as pd
from sentence_transformers import SentenceTransformer
import ast

def generate_vectors(input_csv_path, output_csv_path, model_name='all-MiniLM-L6-v2'):
    # Load mô hình
    model = SentenceTransformer(model_name)

    # Đọc file CSV gốc
    df = pd.read_csv(input_csv_path)

    # Gộp headline và short_description
    df['text'] = df['headline'].fillna('') + ". " + df['short_description'].fillna('')

    # Mã hóa text thành vector
    print("🔄 Đang tạo embedding, vui lòng chờ...")
    embeddings = model.encode(df['text'].tolist(), show_progress_bar=True)

    # Ghi ra file CSV mới với id và vector
    output_df = pd.DataFrame({
        'id': df['id'],
        'vector': [list(vec) for vec in embeddings]  # Convert numpy array to list
    })

    output_df.to_csv(output_csv_path, index=False)
    print(f"✅ Đã lưu file vector tại: {output_csv_path}")

# Ví dụ sử dụng
if __name__ == "__main__":
    input_csv_path = "WebScrapData_rows.csv"
    output_csv_path = "vectors.csv"
    generate_vectors(input_csv_path, output_csv_path)

