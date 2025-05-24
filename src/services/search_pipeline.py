from typing import List, Tuple
import logging
import time
from src.models.search_models import (
    SearchRequest,
    UnifiedSearchResponse,
    KeywordSearchResult,
    SemanticSearchResult,
    CombinedSearchResult
)
from src.services.query_processor import QueryProcessor
from src.services.keyword_search import KeywordSearch
from src.services.semantic_search import SemanticSearch
from src.services.rrf_merger import RRFMerger
from src.services.result_ranker import ResultRanker
import asyncio

logger = logging.getLogger(__name__)

class SearchPipeline:
    """
    Pipeline chính điều phối toàn bộ quá trình tìm kiếm
    """
    def __init__(self):
        """Khởi tạo pipeline với các thành phần cần thiết"""
        self.query_processor = QueryProcessor()
        self.keyword_search = KeywordSearch()
        self.semantic_search = SemanticSearch()
        self.rrf_merger = RRFMerger()
        self.result_ranker = ResultRanker()

    async def execute_search(self, request: SearchRequest) -> UnifiedSearchResponse:
        """
        Thực hiện tìm kiếm thống nhất, trả về 3 danh sách kết quả riêng biệt
        """
        total_start_time = time.time()

        # Xử lý truy vấn
        processed_query = self.query_processor.process(request.query)

        # Thực hiện tìm kiếm song song
        keyword_task = asyncio.create_task(
            self.keyword_search.search(processed_query)
        )
        semantic_task = asyncio.create_task(
            self.semantic_search.search(processed_query)
        )

        # Đợi cả hai tác vụ hoàn thành
        keyword_response, semantic_response = await asyncio.gather(
            keyword_task, semantic_task
        )

        # Bắt đầu tính thời gian RRF
        rrf_start_time = time.time()

        # Kết hợp kết quả bằng RRF
        merged_results = self.rrf_merger.merge(
            keyword_response.results,
            semantic_response.results
        )

        # Sắp xếp và gán thứ hạng
        ranked_results = self.result_ranker.rank(merged_results)

        # Phân trang kết quả RRF
        start_idx = (request.page - 1) * request.page_size
        end_idx = start_idx + request.page_size
        paginated_results = ranked_results[start_idx:end_idx]

        # Tính thời gian xử lý
        rrf_time = (time.time() - rrf_start_time) * 1000
        total_time = (time.time() - total_start_time) * 1000

        # Trả về kết quả thống nhất với 3 danh sách
        return UnifiedSearchResponse(
            # Kết quả tìm kiếm từ khóa
            keyword_results=keyword_response.results,
            total_keyword=keyword_response.total,
            keyword_time_ms=keyword_response.processing_time_ms,
            
            # Kết quả tìm kiếm ngữ nghĩa
            semantic_results=semantic_response.results,
            total_semantic=semantic_response.total,
            semantic_time_ms=semantic_response.processing_time_ms,
            
            # Kết quả RRF
            rrf_results=paginated_results,
            total_rrf=len(ranked_results),
            rrf_time_ms=rrf_time,
            
            # Thông tin phân trang
            page=request.page,
            page_size=request.page_size,
            
            # Thời gian xử lý tổng
            total_time_ms=total_time
        ) 