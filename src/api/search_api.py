from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from src.models.search_models import (
    SearchRequest,
    UnifiedSearchResponse,
    CombinedSearchResult
)
from src.services.search_pipeline import SearchPipeline
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
search_pipeline = SearchPipeline()

@router.post("/search", response_model=UnifiedSearchResponse)
async def search(request: SearchRequest):
    """
    API endpoint thống nhất cho tìm kiếm
    Trả về 3 danh sách kết quả: từ khóa, ngữ nghĩa và kết quả RRF
    
    Args:
        request: SearchRequest chứa truy vấn tìm kiếm và tham số phân trang
    
    Returns:
        UnifiedSearchResponse chứa kết quả từ khóa, ngữ nghĩa và RRF
    """
    try:
        logger.info(f"Nhận yêu cầu tìm kiếm: {request.dict()}")
        results = await search_pipeline.execute_search(request)
        logger.info(
            f"Hoàn thành tìm kiếm:\n"
            f"1. Kết quả từ khóa:\n"
            f"   - Số lượng: {results.total_keyword} kết quả\n"
            f"   - Thời gian: {results.keyword_time_ms:.2f}ms\n"
            f"2. Kết quả ngữ nghĩa:\n"
            f"   - Số lượng: {results.total_semantic} kết quả\n"
            f"   - Thời gian: {results.semantic_time_ms:.2f}ms\n"
            f"3. Kết quả RRF:\n"
            f"   - Số lượng: {results.total_rrf} kết quả\n"
            f"   - Trang: {results.page}/{results.page_size}\n"
            f"   - Thời gian: {results.rrf_time_ms:.2f}ms\n"
            f"Tổng thời gian xử lý: {results.total_time_ms:.2f}ms"
        )
        return results
    except Exception as e:
        logger.error(f"Lỗi tìm kiếm: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xử lý tìm kiếm: {str(e)}"
        )

@router.get("/search", response_model=UnifiedSearchResponse)
async def search_get(
    query: str = Query(..., description="Truy vấn tìm kiếm"),
    page: Optional[int] = Query(1, ge=1, description="Số trang kết quả"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Số kết quả mỗi trang")
):
    """
    API endpoint GET cho tìm kiếm
    Trả về 3 danh sách kết quả: từ khóa, ngữ nghĩa và kết quả RRF
    
    Args:
        query: Truy vấn tìm kiếm
        page: Số trang kết quả (mặc định = 1)
        page_size: Số kết quả mỗi trang (mặc định = 10)
    
    Returns:
        UnifiedSearchResponse chứa kết quả từ khóa, ngữ nghĩa và RRF
    """
    request = SearchRequest(query=query, page=page, page_size=page_size)
    return await search(request)

@router.get("/search/reranked", response_model=list[CombinedSearchResult])
async def search_reranked_get(
    query: str = Query(..., description="Truy vấn tìm kiếm"),
    page: Optional[int] = Query(1, ge=1, description="Số trang kết quả"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Số kết quả mỗi trang")
):
    """
    API endpoint chỉ trả về kết quả đã rerank bằng RRF
    
    Args:
        query: Truy vấn tìm kiếm
        page: Số trang kết quả (mặc định = 1)
        page_size: Số kết quả mỗi trang (mặc định = 10)
    
    Returns:
        Danh sách CombinedSearchResult đã được rerank
    """
    request = SearchRequest(query=query, page=page, page_size=page_size)
    full_results = await search(request)
    return full_results.rrf_results
