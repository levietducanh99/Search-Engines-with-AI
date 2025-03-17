from src.utils.db_connect import get_supabase_client
from rank_bm25 import BM25Okapi
import time


def search(query: str):
    supabase = get_supabase_client()
    start_time = time.time()

    # Exact Match tìm trong headline
    exact_match_response = (supabase.table("WebScrapData")
                            .select("headline")
                            .ilike("headline", f"%{query}%")
                            .execute())

    exact_match_results = exact_match_response.data if exact_match_response.data else []

    # BM25 tìm kiếm trên tất cả dữ liệu
    response = supabase.table("WebScrapData").select("headline").execute()

    if not response.data:
        return exact_match_results, [], time.time() - start_time

    # Tokenize dữ liệu để dùng BM25
    headlines = [row["headline"] for row in response.data]
    tokenized_corpus = [headline.lower().split() for headline in headlines]

    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()

    # Tính điểm BM25
    scores = bm25.get_scores(tokenized_query)
    bm25_results = [(response.data[i], score) for i, score in enumerate(scores) if score > 0]

    # Sắp xếp BM25 theo điểm giảm dần
    bm25_results.sort(key=lambda x: x[1], reverse=True)

    execution_time = time.time() - start_time

    return exact_match_results, bm25_results, execution_time


if __name__ == "__main__":
    query = " new book dog cat"
    exact_matches, bm25_results, execution_time = search(query)

    print("\n🔍 Exact Match Results:")
    for result in exact_matches:
        print(f"✅ {result['headline']}")

    print("\n📊 BM25 Ranked Results:")
    for result, score in bm25_results:
        print(f"⭐ BM25 Score: {score:.4f} | {result['headline']}")

    print(f"\n⏱ Thời gian thực thi: {execution_time:.4f} giây")
