import os

# Định nghĩa cấu trúc thư mục
structure = {
    "": {  # Thay vì "search-engine-project", để rỗng để tạo trực tiếp trong thư mục hiện tại
        "data": {
            "raw": ["articles.json"],
            "processed": ["keywords.json", "embeddings.pkl"]
        },
        "src": {
            "database": {
                "migrations": ["001_create_articles.sql", "002_add_keywords.sql", "003_add_vectors.sql"],
                "queries": ["exact_match.sql", "full_text.sql", "fuzzy_search.sql", "semantic_search.sql"]
            },
            "search_methods": ["exact_match.py", "keyword_search.py", "full_text.py", "fuzzy_search.py", "synonym_search.py", "semantic_search.py"],
            "utils": ["db_connect.py", "preprocess.py", "evaluate.py"]
        },
        "supabase": ["config.toml", "docker-compose.yml"],
        "tests": ["test_exact_match.py", "test_semantic_search.py"],
        "docs": ["README.md", "methods.md"],
        "": ["requirements.txt", "main.py"]
    }
}

# Hàm tạo thư mục và file
def create_structure(base_path, structure):
    for folder, content in structure.items():
        path = os.path.join(base_path, folder) if folder else base_path
        os.makedirs(path, exist_ok=True)
        if isinstance(content, list):
            for file in content:
                open(os.path.join(path, file), 'w').close()
        elif isinstance(content, dict):
            create_structure(path, content)

# Chạy hàm để tạo cấu trúc
create_structure(".", structure)

print("Đã tạo xong cấu trúc thư mục.")