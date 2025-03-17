from src.utils.db_connect import get_supabase_client
import time


def search(query: str):
    # Khởi tạo Supabase client
    supabase = get_supabase_client()

    # Đo thời gian bắt đầu
    start_time = time.time()

    # Tìm kiếm giá trị trong cột name của bảng WebScrapData
    response = supabase.table("WebScrapData").select("headline").ilike("headline", f"%{query}%").execute()

    # Đo thời gian kết thúc
    end_time = time.time()

    # Tính thời gian thực thi (tính bằng giây)
    execution_time = end_time - start_time

    # Kiểm tra kết quả
    if not response.data:
        return [], execution_time

    return response.data, execution_time


if __name__ == "__main__":
    # Test phương pháp Exact Match với bảng WebScrapData
    query = "Student"
    results, execution_time = search(query)
    print("Exact Match Results from WebScrapData:")
    for result in results:
        print(f"Name: {result['headline']}")
    print(f"Thời gian thực thi: {execution_time:.4f} giây")