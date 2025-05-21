from pydantic import BaseModel  # Added import for BaseModel
from typing import Optional, List  # Added import for List

class SearchRequest(BaseModel):
    """
    Model cho yêu cầu tìm kiếm
    """
    query: str  # Truy vấn không được để trống
    page: Optional[int] = 1
    page_size: Optional[int] = 10

    @classmethod
    def validate(cls, values):
        if not values.get("query"):
            raise ValueError("Truy vấn không được để trống.")
        return values


class SearchResult(BaseModel):
    """
    Model cho từng kết quả tìm kiếm
    """
    id: str
    title: str
    bm25_score: float = 0.0
    semantic_score: float = 0.0
    rrf_score: float
    ranking: int

class SearchResponse(BaseModel):
    """
    Model cho phản hồi tìm kiếm
    """
    results: List[SearchResult]
    total: int
    page: int
    page_size: int
    processing_time_ms: float

