from fastapi import APIRouter, HTTPException  # Import APIRouter
from src.models.search_models import SearchRequest, SearchResponse
from src.services.search_pipeline import SearchPipeline
import logging

logger = logging.getLogger(__name__)
router = APIRouter()  # Initialize the router
search_pipeline = SearchPipeline()  # Initialize the search pipeline

@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    API endpoint duy nhất cho toàn bộ quá trình tìm kiếm
    """
    try:
        logger.info(f"Nhận yêu cầu tìm kiếm: {request.dict()}")  # Log request body
        results = await search_pipeline.execute(request)
        logger.info(f"Hoàn thành tìm kiếm. Tìm thấy {results.total} kết quả")
        return results
    except Exception as e:
        logger.error(f"Lỗi tìm kiếm: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xử lý tìm kiếm: {str(e)}"
        )

