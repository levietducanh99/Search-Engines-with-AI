import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from collections import Counter
import string
# push test
# Tải stopwords nếu chưa có
nltk.download("stopwords")

def clean_column_names(df):
    """Chuẩn hóa tên cột (viết thường, xóa khoảng trắng, thay dấu cách bằng `_`)"""
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    return df

def load_data(file_path):
    """Đọc file CSV & chuẩn hóa dữ liệu"""
    df = pd.read_csv(file_path, encoding="utf-8", dtype=str)
    df = clean_column_names(df)

    required_columns = {"link", "headline", "category", "short_description", "authors", "date", "keywords"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        print(f"Lỗi: Thiếu các cột bắt buộc: {missing_columns}")

    # Hiển thị thông tin cơ bản
    print("\nCác cột trong file CSV:", df.columns.tolist())
    print("\nTổng số bản ghi:", len(df))
    print("\nCác trường dữ liệu bị thiếu:\n", df.isnull().sum()[df.isnull().sum() > 0])

    return df

def category_distribution(df):
    """Vẽ biểu đồ phân bố chuyên mục"""
    if "category" not in df.columns:
        print("Lỗi: Cột 'category' không tồn tại!")
        return

    plt.figure(figsize=(10, 5))
    sns.countplot(y=df["category"], order=df["category"].value_counts().index, hue=df["category"], legend=False, palette="coolwarm")
    plt.xlabel("Count")
    plt.ylabel("Category")
    plt.title("Category")
    plt.show()

def analyze_title_length(df):
    """Phân tích độ dài tiêu đề"""
    if "headline" not in df.columns:
        print("Lỗi: Không tìm thấy cột 'headline'!")
        return

    df["title_length"] = df["headline"].dropna().apply(lambda x: len(x.split()))

    print("\nĐộ dài tiêu đề trung bình:", df["title_length"].mean())

    plt.figure(figsize=(10, 5))
    sns.histplot(df["title_length"], bins=30, kde=True, color="blue")
    plt.xlabel("Số từ trong tiêu đề")
    plt.ylabel("Tần suất")
    plt.title("Phân phối độ dài tiêu đề")
    plt.show()

def preprocess_text(text):
    """Xóa dấu câu, stopwords, chuyển về chữ thường"""
    stop_words = set(stopwords.words("english"))
    text = text.translate(str.maketrans("", "", string.punctuation))  # Xóa dấu câu
    words = text.lower().split()
    return words, [word for word in words if word not in stop_words]  # Trả về (toàn bộ từ, từ không có stopwords)

def word_frequency_analysis(df):
    """Phân tích tần suất từ trong tiêu đề"""
    if "headline" not in df.columns:
        print("Lỗi: Không tìm thấy cột 'headline'!")
        return

    text_data = df["headline"].dropna().astype(str)

    # Xử lý văn bản
    all_words, words_no_stopwords = [], []
    for text in text_data:
        words, clean_words = preprocess_text(text)
        all_words.extend(words)
        words_no_stopwords.extend(clean_words)

    # Thống kê stopwords
    total_words = len(all_words)
    stopword_count = total_words - len(words_no_stopwords)
    stopword_ratio = stopword_count / total_words * 100

    print("\nTổng số từ:", total_words)
    print("Số từ là stopwords:", stopword_count)
    print(f"Tỷ lệ stopwords: {stopword_ratio:.2f}%")

    # Đa dạng ngữ nghĩa
    unique_words = set(words_no_stopwords)
    print(f"Số lượng từ duy nhất (không tính stopwords): {len(unique_words)}")
    print(f"Tỷ lệ đa dạng ngữ nghĩa: {len(unique_words) / len(words_no_stopwords) * 100:.2f}%")

    # Đếm tần suất từ
    word_counts = Counter(words_no_stopwords)
    most_common_words = word_counts.most_common(10)

    print("\n10 từ xuất hiện nhiều nhất (loại bỏ stopwords):")
    for word, freq in most_common_words:
        print(f"{word}: {freq}")

    # Vẽ biểu đồ
    words, counts = zip(*most_common_words)
    plt.figure(figsize=(10, 5))
    sns.barplot(x=list(counts), y=list(words), hue=list(words), dodge=False, legend=False, palette="magma")
    plt.xlabel("Tần suất")
    plt.ylabel("Từ khóa")
    plt.title("Top 10 từ xuất hiện nhiều nhất")
    plt.show()

def run_analysis(file_path):
    """Chạy toàn bộ quá trình phân tích"""
    df = load_data(file_path)
    category_distribution(df)
    analyze_title_length(df)
    word_frequency_analysis(df)

# Chạy phân tích với file CSV
run_analysis("WebScrapData_rows.csv")
