# rrf.py

from typing import List, Dict, Tuple


def rrf_fusion(rankings: List[List[Dict]], k: int = 60) -> List[Tuple[Dict, float]]:
    """
    rankings: List các list kết quả.
              Mỗi list là danh sách các dict object {"id": ..., "name": ..., "category": ...}
    k: tham số nhỏ để làm mượt (default = 60)

    Return: List các tuple (document, score) đã xếp hạng.
    """
    scores = {}
    documents = {}

    for ranking in rankings:
        for rank, doc in enumerate(ranking):
            doc_id = doc["id"]
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
            documents[doc_id] = doc  # Lưu lại document theo id

    # Sắp xếp theo tổng điểm giảm dần
    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Trả về danh sách document đã xếp hạng
    return [(documents[doc_id], score) for doc_id, score in sorted_docs]
