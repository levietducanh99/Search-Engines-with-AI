from src.utils.db_connect import get_supabase_client
from rank_bm25 import BM25Okapi
import time

def search(query: str):

    ##########
    # Khởi tạo Supabase client
    supabase = get_supabase_client()

    # Đo thời gian bắt đầu
    start_time = time.time() hellllllll

    # Lấy tất cả dữ liệu từ bảng WebScrapData
    response = supabase.table("WebScrapData").select("name").execute()

    # Kiểm tra dữ liệu trả về
    if not response.data:
        return [], 0.0

    # Trích xuất cột name thành một danh sách (corpus)
    corpus = [row["name"] for row in response.data]

    # Tokenize corpus (BM25 yêu cầu danh sách từ)
    tokenized_corpus = [doc.lower().split(" ") for doc in corpus]

    # Khởi tạo BM25
    bm25 = BM25Okapi(tokenized_corpus)

    # Tokenize truy vấn
    tokenized_query = query.lower().split(" ")

    # Tính điểm BM25 cho từng bản ghi
    scores = bm25.get_scores(tokenized_query)

    # Kết hợp dữ liệu và điểm số, sau đó sắp xếp theo điểm giảm dần
    ranked_results = sorted(zip(response.data, scores), key=lambda x: x[1], reverse=True)

    # Chỉ lấy các bản ghi có điểm lớn hơn 0 (tức là có liên quan)
    filtered_results = [result for result, score in ranked_results if score > 0]

    # Đo thời gian kết thúc
    end_time = time.time()

    # Tính thời gian thực thi
    execution_time = end_time - start_time

    return filtered_results, execution_time

if __name__ == "__main__":
    # Test phương pháp Exact Match với BM25
    query = "hello"
    results, execution_time = search(query)
    print("Exact Match Results with BM25 from WebScrapData:")
    for result in results:
        print(f"Name: {result['name']}")
    print(f"Thời gian thực thi: {execution_time:.4f} giây")