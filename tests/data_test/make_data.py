from src.utils.db_connect import get_supabase_client  # Import get_supabase_client function
from tests.vectorize import vectorize_texts
import pandas as pd
import numpy as np

# Initialize Supabase client
supabase = get_supabase_client()


def fetch_supabase_data(table_name, batch_size=1000):
    """Lấy toàn bộ dữ liệu từ Supabase theo lô"""
    all_data = []
    offset = 0

    while True:
        try:
            # Truy vấn lô dữ liệu với range
            response = supabase.table(table_name).select("id, headline, short_description").range(offset,
                                                                                                  offset + batch_size - 1).execute()

            if not response.data:
                break  # Không còn dữ liệu

            all_data.extend(response.data)
            offset += batch_size
            print(f"Fetched {len(all_data)} rows so far...")

        except Exception as e:
            print(f"Error fetching data at offset {offset}: {str(e)}")
            break

    return all_data


def create_csv_database(table_name, output_file, batch_size=1000):
    """Tạo file CSV từ dữ liệu Supabase"""

    # Lấy toàn bộ dữ liệu
    print("Fetching data from Supabase...")
    rows = fetch_supabase_data(table_name, batch_size)

    if not rows:
        print("No data to process.")
        return

    # Chuẩn bị dữ liệu cho CSV
    data = []
    batch_texts = []
    batch_ids = []

    print("Processing and vectorizing data...")
    for row in rows:
        # Xử lý None
        headline = row['headline'] or ""
        short_desc = row['short_description'] or ""
        combine_text = headline + ': ' + short_desc

        batch_texts.append(combine_text)
        batch_ids.append(row['id'])

        # Xử lý theo lô để tối ưu vector hóa
        if len(batch_texts) >= batch_size:
            # Vector hóa lô
            vectors = vectorize_texts(batch_texts)

            # Thêm vào danh sách
            for id_, vector in zip(batch_ids, vectors):
                vector_str = np.array2string(vector, separator=',', threshold=np.inf, precision=4)
                data.append({'id': id_, 'vector': vector_str})

            batch_texts = []
            batch_ids = []
            print(f"Processed {len(data)} rows...")

    # Xử lý lô cuối (nếu có)
    if batch_texts:
        vectors = vectorize_texts(batch_texts)
        for id_, vector in zip(batch_ids, vectors):
            vector_str = np.array2string(vector, separator=',', threshold=np.inf, precision=4)
            data.append({'id': id_, 'vector': vector_str})

    # Lưu vào CSV
    print("Saving to CSV...")
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"CSV file saved as {output_file}")
    print(f"Total rows processed: {len(df)}")

if __name__ == '__main__':
    table_name = 'WebScrapData'  # Replace with your table name
    output_file = "database.csv"  # Tên file CSV đầu ra
    create_csv_database(table_name, output_file)
    # rows = get_all_rows(table_name)
    # for row in rows:
    #     print(row ["id"], ":", row['headline'])
