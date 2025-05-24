from fastapi import APIRouter, HTTPException
from src.models.search_models import (
    SearchRequest,
    UnifiedSearchResponse
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

