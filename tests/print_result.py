import time  # Import time module
from src.utils.db_connect import get_supabase_client  # Import get_supabase_client function
from tests.vectorize import vectorize_texts, calculate_cosine_similarity
import pandas as pd
import numpy as np
import ast

# Initialize Supabase client
supabase = get_supabase_client()


def compare_with_csv(input_text, csv_file):
    start_time = time.time()  # Start timing

    # Vector hóa chuỗi đầu vào
    input_vector = vectorize_texts(input_text)

    # Đọc file CSV
    df = pd.read_csv(csv_file)

    # Danh sách lưu kết quả
    similarities = []

    # Duyệt qua từng dòng trong CSV
    for index, row in df.iterrows():
        # Chuyển chuỗi vector về mảng NumPy
        vector = np.array(ast.literal_eval(row['vector']))

        # Tính cosine similarity
        similarity = calculate_cosine_similarity(input_vector, vector)

        # Lưu id và độ tương đồng
        similarities.append({'id': row['id'], 'similarity': similarity})

    # Sắp xếp theo độ tương đồng (giảm dần)
    similarities = sorted(similarities, key=lambda x: x['similarity'], reverse=True)

    end_time = time.time()  # End timing
    print(f"Execution time: {end_time - start_time:.4f} seconds")  # Print execution time

    return similarities


def query_supabase_by_ids(table_name, ids):
    try:
        # Truy vấn Supabase với điều kiện id trong danh sách ids
        response = supabase.table(table_name).select("id, headline, short_description").in_("id", ids).execute()

        # Kiểm tra dữ liệu trả về
        if response.data:
            return response.data
        else:
            print(f"No data found for IDs {ids} in table {table_name}")
            return []

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None


# Ví dụ sử dụng
if __name__ == "__main__":
    table_name = "WebScrapData"  # Tên bảng trong Supabase
    input_text = "NRA TV Host Chides Mark Hamill: What If Galactic Republic Outlawed Lightsabers?"
    csv_file_path = "data_test/database.csv"

    # In kết quả
    # Bước 1: So sánh vector và lấy top 5 ID
    similarities = compare_with_csv(input_text, csv_file_path)

    if similarities:
        print("Top similar vectors:")
        ids = [result['id'] for result in similarities]
        for result in similarities[:5]:
            print(f"ID: {result['id']}, Similarity: {result['similarity']:.4f}")

        # Bước 2: Truy vấn Supabase với danh sách ID
        results = query_supabase_by_ids(table_name, ids[:5])  # Lấy top 5 ID

        if results:
            print("\nSupabase query results:")
            for row in results:
                print(f"ID: {row['id']}, Headline: {row['headline']}, Short Description: {row['short_description']}")
    else:
        print("No similar vectors found.")
