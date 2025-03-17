from src.utils.db_connect import get_supabase_client
from rank_bm25 import BM25Okapi
import time
from typing import List, Tuple


def search(query: str) -> Tuple[List[Tuple[dict, float]], float]:
    # Khởi tạo Supabase client
    supabase = get_supabase_client()

    # Đo thời gian bắt đầu
    start_time = time.time()

    # Lấy tất cả dữ liệu từ bảng WebScrapData
    response = supabase.table("WebScrapData").select("headline").execute()

    # Đo thời gian kết thúc truy vấn Supabase
    fetch_time = time.time()

    # Kiểm tra nếu không có dữ liệu
    if not response.data:
        return [], fetch_time - start_time

    # Tách headlines thành danh sách và tokenize
    headlines = [row["headline"] for row in response.data]
    tokenized_corpus = [headline.lower().split() for headline in headlines]

    # Khởi tạo BM25 với corpus đã tokenize
    bm25 = BM25Okapi(tokenized_corpus)

    # Tokenize truy vấn
    tokenized_query = query.lower().split()

    # Tính điểm BM25 cho từng headline
    scores = bm25.get_scores(tokenized_query)

    # Kết hợp điểm số với dữ liệu gốc
    ranked_results = [(response.data[i], score) for i, score in enumerate(scores)]

    # Sắp xếp theo score (giảm dần)
    ranked_results.sort(key=lambda x: x[1], reverse=True)

    # Lấy danh sách kết quả đã sắp xếp, chỉ giữ các kết quả có điểm > 0
    final_results = [(result, score) for result, score in ranked_results if score > 0]

    # Đo thời gian kết thúc toàn bộ quá trình
    end_time = time.time()
    execution_time = end_time - start_time

    return final_results, execution_time


if __name__ == "__main__":
    # Test phương pháp BM25 với bảng WebScrapData
    query = "Book"
    results, execution_time = search(query)
    print("BM25 Search Results from WebScrapData:")
    for result, score in results:
        print(f"BM25 Score: {score:.4f} | Headline: {result['headline']}")
    print(f"Thời gian thực thi: {execution_time:.4f} giây")
