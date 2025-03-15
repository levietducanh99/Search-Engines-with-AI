from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Tải biến môi trường từ file .env
load_dotenv()

# Lấy thông tin Supabase từ biến môi trường
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Khởi tạo Supabase client
def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL and Key must be set in .env file")
    return create_client(SUPABASE_URL, SUPABASE_KEY)