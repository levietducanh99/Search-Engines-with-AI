from services.query_processing import queryProcessing
from services.keyword_search_fakeResult import keywordSearch  # Fixed import
from services.semantic_search import semanticSearch
from services.rerank import combineResults
from models.search_models import SearchResult
from typing import List  # Added import for List

def run_pipeline(query: str) -> List[SearchResult]:  # Fixed type hint
    clean_query = queryProcessing(query)
    bm25_results = keywordSearch(clean_query)
    semantic_results = semanticSearch(clean_query)
    final_results = combineResults(bm25_results, semantic_results)

    # Chuyển dict → SearchResult object
    return [SearchResult(**item) for item in final_results]

