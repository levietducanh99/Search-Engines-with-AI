from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.search_api import router as search_router
import logging

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Tạo FastAPI app
app = FastAPI(
    title="Search Engine API",
    description="API cho tìm kiếm kết hợp từ khóa và ngữ nghĩa",
    version="1.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Đăng ký router
app.include_router(search_router)  # Removed the prefix="/api" to avoid duplication

@app.on_event("startup")
async def startup_event():
    """
    Khởi tạo services khi khởi động
    """
    logger.info("Đang khởi động Search Engine API...")

@app.get("/health")
async def health_check():
    """
    Endpoint kiểm tra trạng thái
    """
    return {"status": "healthy"}

