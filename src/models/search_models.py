from pydantic import BaseModel
from typing import List

class SearchResult(BaseModel):
    title: str
    ranking: int
    bm25_score: float
    semantic_score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
