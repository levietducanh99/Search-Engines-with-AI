from fastapi import APIRouter
from models.search_models import SearchResult, SearchResponse
router = APIRouter()

@router.get("/search", response_model=SearchResponse)
def search_articles(query: str):
    # Mock kết quả để test giao diện
    mock_results = [
        SearchResult(title="How AI is Changing the World", ranking=1, bm25_score=12.5, semantic_score=0.85),
        SearchResult(title="Impact of Technology on Jobs", ranking=2, bm25_score=11.2, semantic_score=0.80),
        SearchResult(title="Future of Work in the AI Era", ranking=3, bm25_score=10.7, semantic_score=0.78),
    ]
    return SearchResponse(results=mock_results)
