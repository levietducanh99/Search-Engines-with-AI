import pandas as pd
import numpy as np
import torch
import time
import logging
import asyncio
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util
import ast
import os

from src.models.search_models import SemanticSearchResult, SemanticSearchResponse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SemanticSearch:
    """
    Class thực hiện tìm kiếm ngữ nghĩa sử dụng mô hình Sentence Transformers
    """
    def __init__(self,
                 model_name: str = "all-MiniLM-L6-v2",
                 vector_path: str = None,
                 csv_path: str = None,
                 data_path: str = None,
                 use_npy: bool = True):
        """
        Khởi tạo với các tham số cho semantic search

        Args:
            model_name: Tên mô hình sentence transformer
            vector_path: Đường dẫn đến file npy chứa vectors
            csv_path: Đường dẫn đến file csv chứa vectors
            data_path: Đường dẫn đến file csv chứa dữ liệu
            use_npy: Có sử dụng file npy không
        """
        self.model_name = model_name
        self.use_npy = use_npy
        self.model = None
        self.corpus_embeddings = None
        self.corpus_ids = None
        self.document_data = None

        # Định nghĩa base path tương đối đến thư mục gốc dự án
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        data_dir = os.path.join(root_dir, "tests", "data_test")

        # Thiết lập đường dẫn mặc định nếu không được truyền vào
        self.vector_path = vector_path or os.path.join(data_dir, "vectors.npy")
        self.csv_path = csv_path or os.path.join(data_dir, "vectors_clean.csv")
        self.data_path = data_path or os.path.join(data_dir, "WebScrapData_rows.csv")

        # Log thông tin đường dẫn
        logger.info(f"Using vector file: {self.vector_path}")
        logger.info(f"Using CSV file: {self.csv_path}")
        logger.info(f"Using data file: {self.data_path}")

        
    async def _load_model(self):
        """Load mô hình sentence transformer"""
        if self.model is None:
            logger.info(f"Loading model: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
        return self.model
    
    async def _load_embeddings(self):
        """Load vectors từ file npy hoặc csv"""
        if self.corpus_embeddings is None:
            if self.use_npy and os.path.exists(self.vector_path):
                logger.info("Loading vectors from NPY...")
                embeddings = torch.from_numpy(np.load(self.vector_path))
                df = pd.read_csv(self.csv_path)
                ids = df["id"].tolist()
            else:
                logger.info("Loading vectors from CSV...")
                df = pd.read_csv(self.csv_path)
                vectors = df["vector"].apply(ast.literal_eval).tolist()
                ids = df["id"].tolist()
                embeddings = torch.tensor(vectors, dtype=torch.float32)
            
            self.corpus_embeddings = util.normalize_embeddings(embeddings)
            self.corpus_ids = ids
        
        return self.corpus_embeddings, self.corpus_ids
    
    async def _load_document_data(self):
        """Load dữ liệu tài liệu từ file csv"""
        if self.document_data is None:
            logger.info(f"Loading document data from {self.data_path}...")
            df = pd.read_csv(self.data_path, quotechar='"', on_bad_lines='skip')
            self.document_data = df
        return self.document_data
    
    def _get_documents_by_ids(self, ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Lấy thông tin tài liệu theo ID"""
        df = self.document_data
        filtered_df = df[df['id'].isin(ids)]
        records = filtered_df.to_dict(orient='records')
        return {str(record['id']): record for record in records}
    
    async def search(self, query: str, top_k: int = 10) -> SemanticSearchResponse:
        """
        Thực hiện tìm kiếm ngữ nghĩa và trả về kết quả
        
        Args:
            query: Chuỗi truy vấn tìm kiếm
            top_k: Số lượng kết quả tối đa cần trả về
            
        Returns:
            SemanticSearchResponse chứa danh sách kết quả tìm kiếm ngữ nghĩa
        """
        start_time = time.time()
        
        # Load model, embeddings, và dữ liệu song song
        model, (corpus_embeddings, corpus_ids), _ = await asyncio.gather(
            self._load_model(),
            self._load_embeddings(),
            self._load_document_data()
        )
        
        # Encode query
        logger.info("Encoding query...")
        query_embedding = model.encode(query, convert_to_tensor=True)
        
        # Fix: Reshape query embedding to 2D before normalizing
        # This prevents the "Dimension out of range" error
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
            
        query_embedding = util.normalize_embeddings(query_embedding)
        
        # Thực hiện semantic search
        logger.info("Performing semantic search...")
        hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=top_k)[0]
        
        # Lấy ID của các kết quả
        hit_ids = [str(corpus_ids[hit['corpus_id']]) for hit in hits]
        
        # Lấy thông tin chi tiết của các tài liệu
        document_info = self._get_documents_by_ids(hit_ids)
        
        # Tạo danh sách kết quả theo mô hình
        semantic_results = []
        for hit in hits:
            doc_id = str(corpus_ids[hit['corpus_id']])
            doc_info = document_info.get(doc_id, {})
            
            # Tạo đối tượng kết quả - đã loại bỏ semantic_context và matched_count
            result = SemanticSearchResult(
                id=doc_id,
                title=doc_info.get('headline', 'Unknown Title'),
                content=str(doc_info.get('short_description') or ''),
                semantic_score=float(hit['score'])
            )
            semantic_results.append(result)
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Tạo và trả về phản hồi
        return SemanticSearchResponse(
            results=semantic_results,
            total=len(semantic_results),
            processing_time_ms=execution_time
        )
