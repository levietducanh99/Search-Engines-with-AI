import re

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

def queryProcessing(query: str) -> str:
    query = query.lower()
    query = re.sub(r"[^\w\s]", "", query)
    query = re.sub(r"\s+", " ", query).strip()

    # Bỏ stopwords
    words = query.split()
    filtered = [w for w in words if w not in stop_words]
    return " ".join(filtered)

