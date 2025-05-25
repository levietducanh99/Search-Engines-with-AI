from typing import List, Dict, Any
import logging
import time
import os
import asyncio
from src.models.search_models import (
    SearchRequest,
    UnifiedSearchResponse,
    KeywordSearchResult,
    SemanticSearchResult,
    CombinedSearchResult,
    KeywordSearchResponse
)
from src.services.query_processor import QueryProcessor
from src.services.semantic_search import SemanticSearch
from src.search_methods.rrf import RRFMerger

# Conditional import to handle case when Whoosh index doesn't exist
try:
    from src.services.keyword_search import KeywordSearch
    HAS_WHOOSH_INDEX = True
except Exception as e:
    HAS_WHOOSH_INDEX = False
    logging.warning(f"KeywordSearch initialization will be deferred: {str(e)}")

logger = logging.getLogger(__name__)

class SearchPipeline:
    """
    Pipeline chính điều phối toàn bộ quá trình tìm kiếm
    """
    def __init__(self,
                 index_dir: str = None,
                 model_name: str = "all-MiniLM-L6-v2",
                 vector_path: str = None,
                 csv_path: str = None,
                 data_path: str = None):
        """
        Khởi tạo pipeline với các thành phần cần thiết và đường dẫn đến dữ liệu
        """

        # Đường dẫn tương đối đến thư mục chứa file hiện tại
        root_dir = os.path.dirname(os.path.abspath(__file__))

        # Thiết lập thư mục index mặc định
        if index_dir is None:
            default_index_path = os.path.join(root_dir, "..", "elasticsearch", "whoosh_index")
            if os.path.exists(default_index_path):
                self.index_dir = default_index_path
                logger.info(f"Found Whoosh index at: {default_index_path}")
            else:
                self.index_dir = os.path.join(root_dir, "whoosh_index")
                logger.warning(f"Whoosh index not found, using fallback: {self.index_dir}")
        else:
            self.index_dir = index_dir

        # Thiết lập đường dẫn đến thư mục data_test
        base_data_path = os.path.join(root_dir, "..", "..", "tests", "data_test")
        if not os.path.exists(base_data_path):
            base_data_path = os.path.join(root_dir, "..", "data_test")

        self.vector_path = vector_path or os.path.join(base_data_path, "vectors.npy")
        self.csv_path = csv_path or os.path.join(base_data_path, "vectors_clean.csv")
        self.data_path = data_path or os.path.join(base_data_path, "WebScrapData_rows.csv")

        # Log thông tin đường dẫn cuối cùng
        logger.info(f"Using vector file: {self.vector_path}")
        logger.info(f"Using CSV file: {self.csv_path}")
        logger.info(f"Using data file: {self.data_path}")

        # Khởi tạo các thành phần
        self.query_processor = QueryProcessor()

        # Khởi tạo KeywordSearch với xử lý lỗi
        try:
            if HAS_WHOOSH_INDEX:
                self.keyword_search = KeywordSearch(index_dir=self.index_dir)
                logger.info(f"Keyword search initialized with index: {self.index_dir}")
            else:
                self.keyword_search = None
                logger.warning("Keyword search not available (Whoosh index issue)")
        except Exception as e:
            self.keyword_search = None
            logger.error(f"Failed to initialize keyword search: {str(e)}")

        # Khởi tạo SemanticSearch
        self.semantic_search = SemanticSearch(
            model_name=model_name,
            vector_path=self.vector_path,
            csv_path=self.csv_path,
            data_path=self.data_path
        )
        self.rrf_merger = RRFMerger()

    async def execute_search(self, request: SearchRequest) -> UnifiedSearchResponse:
        """
        Thực hiện tìm kiếm thống nhất, trả về 3 danh sách kết quả riêng biệt

        Args:
            request: SearchRequest chứa truy vấn tìm kiếm và thông tin phân trang

        Returns:
            UnifiedSearchResponse chứa kết quả tìm kiếm từ khóa, ngữ nghĩa và kết hợp
        """
        total_start_time = time.time()

        # Xử lý truy vấn
        processed_query = self.query_processor.process(request.query)
        logger.info(f"Processed query: '{processed_query}' (original: '{request.query}')")

        # Thực hiện tìm kiếm từ khóa (nếu có)
        if self.keyword_search:
            keyword_task = asyncio.create_task(
                self.keyword_search.search(processed_query)
            )
        else:
            # Tạo kết quả trống nếu không có keyword search
            keyword_task = asyncio.create_task(
                asyncio.sleep(0, result=KeywordSearchResponse(
                    results=[],
                    total=0,
                    processing_time_ms=0.0
                ))
            )
            logger.warning("Keyword search skipped (not available)")

        # Thực hiện tìm kiếm ngữ nghĩa
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

        # Phân trang kết quả RRF
        start_idx = (request.page - 1) * request.page_size
        end_idx = start_idx + request.page_size
        paginated_results = merged_results[start_idx:end_idx] if start_idx < len(merged_results) else []

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
            total_rrf=len(merged_results),
            rrf_time_ms=rrf_time,

            # Thông tin phân trang
            page=request.page,
            page_size=request.page_size,

            # Thời gian xử lý tổng
            total_time_ms=total_time
        )

# Hàm này có thể chạy trực tiếp từ IDE
async def run_search(query: str, page: int = 1, page_size: int = 10) -> None:
    """
    Thực hiện tìm kiếm và hiển thị kết quả trực tiếp (không cần chạy server)

    Args:
        query: Truy vấn tìm kiếm
        page: Số trang kết quả (mặc định = 1)
        page_size: Số kết quả mỗi trang (mặc định = 10)
    """
    print("\n" + "=" * 80)
    print(f"🔍 Tìm kiếm: '{query}'")
    print("=" * 80)

    try:
        # Khởi tạo search pipeline
        pipeline = SearchPipeline()

        # Tạo request
        request = SearchRequest(query=query, page=page, page_size=page_size)

        # Thực hiện tìm kiếm
        print("⏳ Đang xử lý tìm kiếm...")
        results = await pipeline.execute_search(request)

        # Hiển thị thông tin tổng quan
        print("\n📊 THÔNG TIN TỔNG QUAN:")
        print(f"- Thời gian xử lý tổng: {results.total_time_ms:.2f}ms")
        print(f"- Kết quả từ khóa: {results.total_keyword} ({results.keyword_time_ms:.2f}ms)")
        print(f"- Kết quả ngữ nghĩa: {results.total_semantic} ({results.semantic_time_ms:.2f}ms)")
        print(f"- Kết quả RRF: {results.total_rrf} ({results.rrf_time_ms:.2f}ms)")
        print(f"- Trang: {results.page}/{(results.total_rrf + results.page_size - 1) // results.page_size}")

        # Hiển thị kết quả RRF (đã kết hợp và xếp hạng lại)
        print("\n🏆 KẾT QUẢ ĐÃ XẾP HẠNG LẠI (RRF):")
        if not results.rrf_results:
            print("  Không có kết quả phù hợp.")
        else:
            for i, result in enumerate(results.rrf_results, 1):
                print(f"\n{i}. {result.title}")
                print(f"   ID: {result.id} | Xếp hạng: {result.ranking}")
                print(f"   BM25: {result.bm25_score:.4f} | Semantic: {result.semantic_score:.4f} | RRF: {result.rrf_score:.4f}")

                if result.content:
                    # Hiển thị tối đa 200 ký tự của nội dung
                    content = result.content[:200] + "..." if len(result.content) > 200 else result.content
                    print(f"   📝 {content}")

                if result.keywords:
                    print(f"   🔑 Từ khóa: {', '.join(result.keywords)}")

                if result.semantic_context:
                    print(f"   🧠 Ngữ cảnh: {' | '.join(result.semantic_context)}")

        return results

    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        logger.error("Error in search pipeline", exc_info=True)
        return None

# Nếu chạy trực tiếp file này
if __name__ == "__main__":
    import sys

    # Thiết lập logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Lấy query từ tham số dòng lệnh hoặc sử dụng mặc định
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        # Truy vấn mặc định nếu không có tham số
        query = "Messi leaves Barcelona"
        print(f"Không có truy vấn, sử dụng truy vấn mặc định: '{query}'")

    # Chạy hàm tìm kiếm
    asyncio.run(run_search(query))

