import re
import logging

try:
    from nltk.corpus import stopwords
except ModuleNotFoundError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk"])
    from nltk.corpus import stopwords

try:
    stop_words = set(stopwords.words('english'))
except LookupError:
    import nltk
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

try:
    from spellchecker import SpellChecker
except ModuleNotFoundError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyspellchecker"])
    from spellchecker import SpellChecker

logger = logging.getLogger(__name__)

class QueryProcessor:
    """
    Class xử lý truy vấn tìm kiếm, bao gồm làm sạch truy vấn, sửa lỗi chính tả và loại bỏ stop words
    """
    def __init__(self):
        """Khởi tạo QueryProcessor"""
        self.stop_words = stop_words
        self.spell_checker = SpellChecker(language='en')

    def correct_spelling(self, text: str) -> str:
        """
        Sửa lỗi chính tả trong truy vấn

        Args:
            text: Chuỗi truy vấn cần sửa lỗi chính tả

        Returns:
            Chuỗi truy vấn đã được sửa lỗi chính tả
        """
        if not text:
            return text

        words = text.split()
        corrected_words = []

        for word in words:
            # Kiểm tra nếu từ có lỗi chính tả
            if word not in self.spell_checker:
                # Lấy từ sửa lỗi gần nhất
                corrected = self.spell_checker.correction(word)
                if corrected:
                    corrected_words.append(corrected)
                else:
                    corrected_words.append(word)
            else:
                corrected_words.append(word)

        return ' '.join(corrected_words)

    def process(self, query: str) -> str:
        """
        Xử lý truy vấn bằng cách sửa lỗi chính tả, làm sạch và loại bỏ stop words

        Args:
            query: Chuỗi truy vấn đầu vào
            
        Returns:
            Chuỗi truy vấn đã được xử lý
        """
        if not query or not isinstance(query, str):
            logger.warning(f"Invalid query: {query}")
            return ""
            
        # Lưu lại truy vấn gốc
        original_query = query

        # Sửa lỗi chính tả
        query = self.correct_spelling(query)
        if query != original_query:
            logger.info(f"Corrected spelling from '{original_query}' to '{query}'")

        # Chuyển về chữ thường
        query = query.lower()
        
        # Loại bỏ ký tự đặc biệt
        query = re.sub(r"[^\w\s]", "", query)
        
        # Loại bỏ khoảng trắng thừa
        query = re.sub(r"\s+", " ", query).strip()

        # Bỏ stopwords
        words = query.split()
        filtered = [w for w in words if w not in self.stop_words]
        
        processed_query = " ".join(filtered)
        
        # Nếu sau khi lọc hết thì giữ nguyên truy vấn gốc
        if not processed_query and query:
            logger.info(f"Query consists only of stopwords, keeping original: '{query}'")
            return query
            
        return processed_query
