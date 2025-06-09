import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from collections import Counter
import string
import numpy as np
from nltk import ngrams
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.cm as cm
import networkx as nx
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk

# Tải các module NLTK cần thiết
nltk.download("stopwords")
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("maxent_ne_chunker")
nltk.download("words")
nltk.download("wordnet")

# Khởi tạo lemmatizer
lemmatizer = WordNetLemmatizer()

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

    print("\n=== PHÂN TÍCH DỮ LIỆU CƠ BẢN ===")
    print("Dữ liệu đã được tải thành công với {} bản ghi và {} cột.".format(len(df), len(df.columns)))
    print("Giải thích: Đây là bước đầu tiên để hiểu cấu trúc dữ liệu, giúp xác định những trường thông tin nào có sẵn.")
    print("Ứng dụng cho tìm kiếm: Việc nắm rõ cấu trúc dữ liệu giúp xác định trường nào cần được đánh chỉ mục cho tìm kiếm từ khóa và tìm kiếm ngữ nghĩa.")

    return df

def category_distribution(df):
    """Vẽ biểu đồ phân bố chuyên mục"""
    if "category" not in df.columns:
        print("Lỗi: Cột 'category' không tồn tại!")
        return

    # Set style
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Create bigger figure with better resolution
    plt.figure(figsize=(16, 12), dpi=100)
    
    # Get category counts for adding values to the end of bars
    cat_counts = df["category"].value_counts()
    
    # Print detailed analysis
    print("\n=== PHÂN TÍCH PHÂN BỐ CHUYÊN MỤC ===")
    print(f"Số lượng chuyên mục khác nhau: {len(cat_counts)}")
    print("Top 5 chuyên mục phổ biến nhất:")
    for idx, (cat, count) in enumerate(cat_counts.head(5).items(), 1):
        print(f"  {idx}. {cat}: {count} bài viết ({count/len(df)*100:.2f}%)")

    print("\nGiải thích: Phân bố chuyên mục cho thấy mức độ đa dạng của dữ liệu và độ phủ từng lĩnh vực.")
    print("Ứng dụng cho tìm kiếm: Có thể cân nhắc điều chỉnh trọng số cho các chuyên mục ít phổ biến để cải thiện kết quả tìm kiếm trên các lĩnh vực này.")

    # Create the plot with vibrant colors
    ax = sns.countplot(
        y=df["category"], 
        order=cat_counts.index, 
        palette="viridis",
        edgecolor="0.2",
        linewidth=1.5
    )
    
    # Add count values at the end of each bar
    for i, v in enumerate(cat_counts):
        ax.text(v + 0.5, i, str(v), va='center', fontweight='bold')
    
    # Adjust grid and styling
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Enhanced titles and labels
    plt.title("Phân bố chuyên mục", fontsize=24, fontweight='bold', pad=20)
    plt.xlabel("Số lượng", fontsize=16, fontweight='bold')
    plt.ylabel("Chuyên mục", fontsize=16, fontweight='bold')

    # Increase tick labels size for better readability
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=14, fontweight='bold')
    
    # Tight layout to make better use of space
    plt.tight_layout()
    plt.show()

def analyze_title_length(df):
    """Phân tích độ dài tiêu đề"""
    if "headline" not in df.columns:
        print("Lỗi: Không tìm thấy cột 'headline'!")
        return

    df["title_length"] = df["headline"].dropna().apply(lambda x: len(x.split()))

    avg_length = df["title_length"].mean()
    median_length = df["title_length"].median()
    std_length = df["title_length"].std()

    print("\n=== PHÂN TÍCH ĐỘ DÀI TIÊU ĐỀ ===")
    print(f"Độ dài tiêu đề trung bình: {avg_length:.2f} từ")
    print(f"Độ dài tiêu đề trung vị: {median_length} từ")
    print(f"Độ lệch chuẩn: {std_length:.2f}")
    print(f"Độ dài tối thiểu: {df['title_length'].min()} từ")
    print(f"Độ dài tối đa: {df['title_length'].max()} từ")

    # Calculate percentiles
    percentiles = [10, 25, 50, 75, 90]
    perc_values = np.percentile(df["title_length"], percentiles)

    print("\nPhân phối độ dài tiêu đề theo phần trăm:")
    for p, v in zip(percentiles, perc_values):
        print(f"  {p}%: {v} từ")

    print("\nGiải thích: Phân tích này giúp hiểu độ dài phổ biến của tiêu đề trong tập dữ liệu.")
    print("Ứng dụng cho tìm kiếm: Tối ưu thuật toán tìm kiếm để phù hợp với độ dài tiêu đề phổ biến.")
    print("  - Tiêu đề ngắn (<5 từ): Cân nhắc tăng trọng số cho mỗi từ khớp")
    print("  - Tiêu đề dài (>10 từ): Có thể giảm ngưỡng khớp tối thiểu")

    plt.figure(figsize=(12, 6))
    ax = sns.histplot(df["title_length"], bins=30, kde=True, color="blue")

    # Highlight average with vertical line
    plt.axvline(x=avg_length, color='r', linestyle='--', linewidth=2, label=f'Trung bình: {avg_length:.2f}')

    # Annotations
    plt.text(avg_length + 0.5, ax.get_ylim()[1]*0.9, f'Trung bình: {avg_length:.2f}',
             verticalalignment='top', color='r', fontweight='bold')

    plt.xlabel("Số từ trong tiêu đề")
    plt.ylabel("Tần suất")
    plt.title("Phân phối độ dài tiêu đề", fontsize=16)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def preprocess_text(text):
    """Xóa dấu câu, stopwords, chuyển về chữ thường"""
    stop_words = set(stopwords.words("english"))
    text = text.translate(str.maketrans("", "", string.punctuation))  # Xóa dấu câu
    words = text.lower().split()
    return words, [word for word in words if word not in stop_words]  # Trả về (toàn bộ từ, từ không có stopwords)

def enhanced_preprocess_text(text):
    """Xử lý văn bản nâng cao: tokenize, loại bỏ stopwords, lemmatize"""
    stop_words = set(stopwords.words("english"))

    # Tokenize
    tokens = word_tokenize(text.lower())

    # Loại bỏ dấu câu và số
    tokens = [word for word in tokens if word.isalpha()]

    # Loại bỏ stopwords
    tokens = [word for word in tokens if word not in stop_words]

    # Lemmatize
    lemmatized = [lemmatizer.lemmatize(word) for word in tokens]

    return lemmatized

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

    print("\n=== PHÂN TÍCH TẦN SUẤT TỪ TRONG TIÊU ĐỀ ===")
    print("Tổng số từ:", total_words)
    print("Số từ là stopwords:", stopword_count)
    print(f"Tỷ lệ stopwords: {stopword_ratio:.2f}%")

    # Đa dạng ngữ nghĩa
    unique_words = set(words_no_stopwords)
    uniqueness_ratio = len(unique_words) / len(words_no_stopwords) * 100
    print(f"Số lượng từ duy nhất (không tính stopwords): {len(unique_words)}")
    print(f"Tỷ lệ đa dạng ngữ nghĩa: {uniqueness_ratio:.2f}%")

    print("\nGiải thích: Phân tích tần suất từ giúp hiểu các từ khóa phổ biến trong dữ liệu.")
    print(f"Tỷ lệ đa dạng ngữ nghĩa {uniqueness_ratio:.2f}% cho thấy mức độ phong phú của từ vựng trong tiêu đề.")
    if uniqueness_ratio > 50:
        print("  → Dữ liệu có tính đa dạng cao, thích hợp cho tìm kiếm semantic.")
    else:
        print("  → Dữ liệu có nhiều từ lặp lại, tìm kiếm từ khóa có thể hiệu quả.")

    # Đếm tần suất từ
    word_counts = Counter(words_no_stopwords)
    most_common_words = word_counts.most_common(15)

    print("\n15 từ xuất hiện nhiều nhất (loại bỏ stopwords):")
    for i, (word, freq) in enumerate(most_common_words, 1):
        coverage = freq / len(words_no_stopwords) * 100
        print(f"{i}. {word}: {freq} ({coverage:.2f}% độ phủ)")

    # Vẽ biểu đồ
    top_words, top_counts = zip(*most_common_words[:10])
    plt.figure(figsize=(12, 6))
    bars = sns.barplot(x=list(top_words), y=list(top_counts), palette="magma")
    plt.xticks(rotation=45, ha='right')

    # Thêm giá trị lên đầu mỗi bar
    for i, count in enumerate(top_counts):
        bars.text(i, count + 5, str(count), ha='center')

    plt.xlabel("Từ khóa", fontsize=12)
    plt.ylabel("Tần suất", fontsize=12)
    plt.title("Top 10 từ xuất hiện nhiều nhất", fontsize=16)
    plt.tight_layout()
    plt.show()

    print("\nỨng dụng cho tìm kiếm: Các từ xuất hiện với tần suất cao nên được đánh trọng số phù hợp trong thuật toán tìm kiếm.")
    print("  - Có thể sử dụng IDF (Inverse Document Frequency) để giảm trọng số cho các từ quá phổ biến")
    print("  - Từ khóa có tần suất trung bình thường mang nhiều giá trị ngữ nghĩa hơn")

def analyze_ngrams(df, n=2, top_n=20):
    """Phân tích n-gram từ tiêu đề và mô tả"""
    if "headline" not in df.columns:
        print("Lỗi: Không tìm thấy cột 'headline'!")
        return

    # Kết hợp tiêu đề và mô tả ngắn (nếu có)
    data = df["headline"].dropna().astype(str).tolist()
    if "short_description" in df.columns:
        data.extend(df["short_description"].dropna().astype(str).tolist())

    # Tiền xử lý dữ liệu
    stop_words = set(stopwords.words("english"))
    processed_texts = []

    for text in data:
        # Loại bỏ dấu câu và chuyển thành chữ thường
        text = text.lower().translate(str.maketrans("", "", string.punctuation))
        # Tokenize
        tokens = word_tokenize(text)
        # Loại bỏ stopwords
        filtered_tokens = [word for word in tokens if word not in stop_words and len(word) > 1]
        processed_texts.append(filtered_tokens)

    # Tạo n-grams
    all_ngrams = []
    for text in processed_texts:
        if len(text) >= n:  # Chỉ tạo n-gram nếu văn bản đủ dài
            text_ngrams = list(ngrams(text, n))
            all_ngrams.extend([" ".join(gram) for gram in text_ngrams])

    # Đếm tần suất ngrams
    ngram_counts = Counter(all_ngrams)
    top_ngrams = ngram_counts.most_common(top_n)

    print(f"\n=== PHÂN TÍCH {n}-GRAM ===")
    print(f"Tổng số {n}-gram duy nhất: {len(ngram_counts)}")
    print(f"\nTop {top_n} {n}-gram xuất hiện nhiều nhất:")

    # In chi tiết
    for i, (ngram, count) in enumerate(top_ngrams, 1):
        print(f"{i}. '{ngram}': {count}")

    print("\nGiải thích: Phân tích n-gram giúp tìm ra các cụm từ hay xuất hiện cùng nhau.")
    print(f"Ứng dụng cho tìm kiếm: Các {n}-gram phổ biến có thể được sử dụng làm từ khóa tìm kiếm.")
    print("  - Cải thiện gợi ý tìm kiếm (search suggestion)")
    print("  - Phát hiện các cụm từ đi liền nhau, giúp nâng cao chất lượng tìm kiếm chính xác")

    # Vẽ biểu đồ
    plt.figure(figsize=(14, 8))
    words = [x[0] for x in top_ngrams[:15]]
    counts = [x[1] for x in top_ngrams[:15]]

    bars = sns.barplot(x=counts, y=words, palette="viridis")

    # Thêm giá trị vào thanh ngang
    for i, count in enumerate(counts):
        bars.text(count + 1, i, str(count), va='center')

    plt.xlabel(f"Tần suất xuất hiện", fontsize=12)
    plt.ylabel(f"{n}-gram", fontsize=12)
    plt.title(f"Top {n}-gram phổ biến nhất", fontsize=16)
    plt.tight_layout()
    plt.show()

def analyze_keyword_co_occurrence(df, top_n=30, min_edge_weight=2):
    """Phân tích đồng xuất hiện của từ khóa bằng đồ thị"""
    if "headline" not in df.columns:
        print("Lỗi: Không tìm thấy cột 'headline'!")
        return

    text_data = df["headline"].dropna().astype(str)

    # Xử lý văn bản
    processed_docs = []
    for text in text_data:
        tokens = enhanced_preprocess_text(text)
        processed_docs.append(tokens)

    # Tính tần suất của từng từ
    all_words = [word for doc in processed_docs for word in doc]
    word_freq = Counter(all_words)

    # Chọn top_n từ phổ biến nhất
    top_words = [word for word, freq in word_freq.most_common(top_n)]

    # Tạo đồ thị đồng xuất hiện
    G = nx.Graph()

    # Đếm đồng xuất hiện các từ
    for doc in processed_docs:
        # Chỉ xem xét các từ trong top_n
        doc_top_words = [word for word in doc if word in top_words]
        # Thêm các từ làm node
        for word in doc_top_words:
            if not G.has_node(word):
                G.add_node(word, weight=word_freq[word])

        # Thêm kết nối giữa các từ đồng xuất hiện
        for i, word1 in enumerate(doc_top_words):
            for j, word2 in enumerate(doc_top_words[i+1:], i+1):
                if G.has_edge(word1, word2):
                    G[word1][word2]['weight'] += 1
                else:
                    G.add_edge(word1, word2, weight=1)

    # Lọc các kết nối quá yếu
    edges_to_remove = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] < min_edge_weight]
    G.remove_edges_from(edges_to_remove)

    print("\n=== PHÂN TÍCH ĐỒNG XUẤT HIỆN TỪ KHÓA ===")
    print(f"Số lượng từ khóa được phân tích: {len(G.nodes())}")
    print(f"Số lượng kết nối đồng xuất hiện: {len(G.edges())}")

    # Tính toán các chỉ số trung tâm
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)

    # In các từ khóa có tính trung tâm cao nhất
    print("\nTop 10 từ khóa có tính kết nối cao nhất:")
    top_degree = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (word, centrality) in enumerate(top_degree, 1):
        print(f"{i}. {word}: {centrality:.4f} (Tần suất: {word_freq[word]})")

    print("\nGiải thích: Phân tích đồng xuất hiện cho thấy mối quan hệ giữa các từ khóa.")
    print("Ứng dụng cho tìm kiếm:")
    print("  - Những từ khóa có tính kết nối cao nên được ưu tiên trong mở rộng truy vấn (query expansion)")
    print("  - Có thể xây dựng gợi ý tìm kiếm dựa trên các cụm từ đồng xuất hiện")
    print("  - Cải thiện tìm kiếm ngữ nghĩa bằng cách kết hợp các từ có liên quan mạnh")

    # Vẽ đồ thị đồng xuất hiện
    plt.figure(figsize=(16, 12))

    # Tính layout
    pos = nx.spring_layout(G, k=0.3, iterations=50)

    # Tính kích thước node dựa trên tần suất từ
    node_sizes = [G.nodes[node]['weight'] * 10 for node in G.nodes()]

    # Tính độ dày cạnh dựa trên trọng số
    edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
    max_edge_weight = max(edge_weights) if edge_weights else 1
    normalized_edge_weights = [2 + 3 * (w / max_edge_weight) for w in edge_weights]

    # Vẽ đồ thị
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=list(degree_centrality.values()),
                          cmap=plt.cm.viridis, alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=normalized_edge_weights, alpha=0.5, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')

    plt.title("Đồ thị đồng xuất hiện từ khóa", fontsize=20, pad=20)
    plt.axis('off')
    plt.colorbar(plt.cm.ScalarMappable(cmap=plt.cm.viridis),
                shrink=0.5,
                label='Tính trung tâm')
    plt.tight_layout()
    plt.show()

def extract_named_entities(df, sample_size=500):
    """Phân tích các thực thể có tên (Named Entities)"""
    if "headline" not in df.columns:
        print("Lỗi: Không tìm thấy cột 'headline'!")
        return

    # Lấy mẫu để tăng tốc độ xử lý
    if len(df) > sample_size:
        text_data = df["headline"].dropna().sample(sample_size, random_state=42).astype(str)
    else:
        text_data = df["headline"].dropna().astype(str)

    # Hợp nhất với short_description nếu có
    if "short_description" in df.columns:
        if len(df) > sample_size:
            desc_data = df["short_description"].dropna().sample(sample_size, random_state=42).astype(str)
        else:
            desc_data = df["short_description"].dropna().astype(str)
        text_data = pd.concat([text_data, desc_data])

    print("\n=== PHÂN TÍCH THỰC THỂ CÓ TÊN (NER) ===")
    print(f"Phân tích dựa trên {len(text_data)} mẫu văn bản")

    # Các loại thực thể cần đếm
    entity_types = {
        'PERSON': 'Tên người',
        'GPE': 'Địa điểm, quốc gia, thành phố',
        'ORGANIZATION': 'Tổ chức',
        'FACILITY': 'Cơ sở vật chất',
        'LOC': 'Vị trí địa lý',
        'PRODUCT': 'Sản phẩm',
        'EVENT': 'Sự kiện',
        'WORK_OF_ART': 'Tác phẩm nghệ thuật',
        'NORP': 'Quốc tịch, tôn giáo, chính trị',
        'TIME': 'Thời gian'
    }

    entity_counts = {entity: 0 for entity in entity_types.keys()}
    all_entities = []

    # Xử lý và phân tích thực thể
    for text in text_data:
        tokens = word_tokenize(text)
        pos_tags = pos_tag(tokens)

        # Trích xuất thực thể
        named_entities = ne_chunk(pos_tags)

        # Đếm thực thể
        for chunk in named_entities:
            if hasattr(chunk, 'label'):
                entity_type = chunk.label()
                entity_text = ' '.join(c[0] for c in chunk)
                all_entities.append((entity_text, entity_type))
                if entity_type in entity_counts:
                    entity_counts[entity_type] += 1

    # In tỷ lệ các loại thực thể
    total_entities = sum(entity_counts.values())
    print(f"\nTổng số thực thể đã nhận diện: {total_entities}")

    if total_entities > 0:
        print("\nPhân bố theo loại thực thể:")
        for entity_type, count in sorted(entity_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"  - {entity_types.get(entity_type, entity_type)}: {count} ({count/total_entities*100:.2f}%)")

        # Đếm các thực thể cụ thể xuất hiện nhiều nhất
        entity_instances = Counter([entity[0].lower() for entity in all_entities])
        print("\nTop 15 thực thể cụ thể xuất hiện nhiều nhất:")
        for i, (entity, count) in enumerate(entity_instances.most_common(15), 1):
            print(f"{i}. {entity}: {count}")

    print("\nGiải thích: Phân tích thực thể có tên (NER) giúp xác định các đối tượng quan trọng trong nội dung.")
    print("Ứng dụng cho tìm kiếm:")
    print("  - Tăng trọng số cho truy vấn khớp với các thực thể có tên")
    print("  - Xây dựng tính năng lọc kết quả theo loại thực thể")
    print("  - Cải thiện tìm kiếm ngữ nghĩa bằng cách hiểu vai trò của thực thể trong văn bản")

    if total_entities > 0:
        # Vẽ biểu đồ phân bố thực thể
        plt.figure(figsize=(12, 6))

        # Lọc các loại thực thể có số lượng > 0
        filtered_entities = {k: v for k, v in entity_counts.items() if v > 0}

        # Sort by count
        sorted_entities = dict(sorted(filtered_entities.items(), key=lambda item: item[1], reverse=True))

        # Create readable labels
        labels = [entity_types.get(entity, entity) for entity in sorted_entities.keys()]

        # Plot
        bars = sns.barplot(x=list(labels), y=list(sorted_entities.values()), palette="viridis")

        # Thêm giá trị lên đầu mỗi bar
        for i, count in enumerate(sorted_entities.values()):
            bars.text(i, count + 1, str(count), ha='center')

        plt.xticks(rotation=45, ha='right')
        plt.xlabel("Loại thực thể")
        plt.ylabel("Số lượng")
        plt.title("Phân bố các loại thực thể có tên")
        plt.tight_layout()
        plt.show()

def analyze_semantic_similarity(df, sample_size=1000):
    """Phân tích độ tương tự ngữ nghĩa giữa các văn bản"""
    if "headline" not in df.columns:
        print("Lỗi: Không tìm thấy cột 'headline'!")
        return

    # Kết hợp tiêu đề và mô tả ngắn để phân tích
    if "short_description" in df.columns:
        df["text_content"] = df["headline"].fillna("") + " " + df["short_description"].fillna("")
    else:
        df["text_content"] = df["headline"]

    # Lấy mẫu để tăng tốc độ xử lý
    if len(df) > sample_size:
        sampled_df = df.dropna(subset=["text_content"]).sample(sample_size, random_state=42)
    else:
        sampled_df = df.dropna(subset=["text_content"])

    # Chuyển sang chuỗi
    documents = sampled_df["text_content"].astype(str).tolist()

    print("\n=== PHÂN TÍCH TƯƠNG TỰ NGỮ NGHĨA ===")
    print(f"Phân tích dựa trên {len(documents)} mẫu văn bản")

    # Sử dụng TF-IDF để biểu diễn văn bản
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Tính ma trận tương tự cosine
    cosine_sim = cosine_similarity(tfidf_matrix)

    # Phân tích độ tương tự
    # Độ tương tự trung bình giữa các văn bản
    avg_similarity = np.mean(cosine_sim)
    # Tỷ lệ các văn bản có mức tương tự cao (>0.5)
    high_sim_ratio = np.sum(cosine_sim > 0.5) / (cosine_sim.shape[0] * cosine_sim.shape[1])

    print(f"\nĐộ tương tự cosine trung bình giữa các văn bản: {avg_similarity:.4f}")
    print(f"Tỷ lệ văn bản có độ tương tự cao (>0.5): {high_sim_ratio:.4f}")

    print("\nPhân phối độ tương tự:")
    sim_thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    for threshold in sim_thresholds:
        ratio = np.sum((cosine_sim >= threshold) & (cosine_sim < threshold + 0.1)) / (cosine_sim.shape[0] * cosine_sim.shape[1])
        print(f"  {threshold:.1f} - {threshold+0.1:.1f}: {ratio:.4f}")

    print("\nGiải thích: Phân tích tương tự ngữ nghĩa giúp đánh giá mức độ khác biệt giữa các văn bản.")
    if avg_similarity > 0.4:
        print("  → Dữ liệu có độ tương đồng cao, có thể tối ưu tìm kiếm ngữ nghĩa.")
    else:
        print("  → Dữ liệu có tính đa dạng cao, cần cân nhắc kết hợp nhiều phương pháp tìm kiếm.")

    print("\nỨng dụng cho tìm kiếm:")
    print("  - Nhóm các văn bản tương tự để cải thiện tính đa dạng của kết quả tìm kiếm")
    print("  - Sử dụng metric tương tự để mở rộng kết quả tìm kiếm liên quan")
    print("  - Cải thiện thuật toán xếp hạng kết quả tìm kiếm")

    # Vẽ biểu đồ phân phối độ tương tự
    plt.figure(figsize=(12, 6))

    # Lấy giá trị trên tam giác trên của ma trận (không tính đường chéo)
    sim_values = []
    for i in range(cosine_sim.shape[0]):
        for j in range(i+1, cosine_sim.shape[1]):
            sim_values.append(cosine_sim[i, j])

    sns.histplot(sim_values, bins=50, kde=True, color="purple")
    plt.xlabel("Độ tương tự cosine")
    plt.ylabel("Tần suất")
    plt.title("Phân phối độ tương tự ngữ nghĩa giữa các văn bản")

    # Vẽ đường trung bình
    plt.axvline(x=avg_similarity, color='red', linestyle='--',
                label=f'Trung bình: {avg_similarity:.4f}')
    plt.legend()

    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

def analyze_search_keywords_quality(df):
    """Phân tích chất lượng từ khóa tìm kiếm trong dữ liệu"""
    if "keywords" not in df.columns:
        print("\n=== PHÂN TÍCH CÁC TỪ KHÓA TÌM KIẾM ===")
        print("Lưu ý: Không tìm thấy cột 'keywords' trong dữ liệu.")
        print("Gợi ý: Bạn có thể tạo từ khóa tự động từ tiêu đề và mô tả ngắn.")

        # Tạo từ khóa tự động
        print("\nĐang tạo từ khóa tự động từ tiêu đề và mô tả ngắn...")

        # Kết hợp tiêu đề và mô tả
        if "headline" in df.columns and "short_description" in df.columns:
            df["combined_text"] = df["headline"].fillna("") + " " + df["short_description"].fillna("")
        elif "headline" in df.columns:
            df["combined_text"] = df["headline"].fillna("")
        else:
            print("Lỗi: Không thể tạo từ khóa vì thiếu cả tiêu đề và mô tả.")
            return

        # Xử lý và trích xuất từ khóa
        auto_keywords = []
        stop_words = set(stopwords.words("english"))

        for text in df["combined_text"].dropna().astype(str):
            # Tiền xử lý văn bản
            tokens = enhanced_preprocess_text(text)

            # Đếm tần suất từ
            word_freq = Counter(tokens)

            # Chọn top 5 từ khóa cho mỗi văn bản
            top_kw = [word for word, _ in word_freq.most_common(5)]
            auto_keywords.append(", ".join(top_kw) if top_kw else "")

        # Gán từ khóa tự động vào DataFrame
        df_sample = df.iloc[:len(auto_keywords)].copy()
        df_sample["keywords"] = auto_keywords

        print(f"Đã tạo từ khóa cho {len(auto_keywords)} bản ghi.")
    else:
        df_sample = df.copy()

    # Tiếp tục phân tích nếu có từ khóa
    if "keywords" in df_sample.columns:
        # Lọc các hàng có từ khóa
        df_keywords = df_sample[df_sample["keywords"].notna() & (df_sample["keywords"] != "")]

        print("\n=== PHÂN TÍCH CÁC TỪ KHÓA TÌM KIẾM ===")
        print(f"Số lượng bản ghi có từ khóa: {len(df_keywords)} / {len(df_sample)} ({len(df_keywords)/len(df_sample)*100:.2f}%)")

        # Phân tích số lượng từ khóa cho mỗi bản ghi
        df_keywords["keyword_count"] = df_keywords["keywords"].astype(str).apply(lambda x: len(x.split(",")))

        avg_kw_count = df_keywords["keyword_count"].mean()
        median_kw_count = df_keywords["keyword_count"].median()
        max_kw_count = df_keywords["keyword_count"].max()

        print(f"\nSố từ khóa trung bình cho mỗi bản ghi: {avg_kw_count:.2f}")
        print(f"Số từ khóa trung vị: {median_kw_count}")
        print(f"Số từ khóa tối đa: {max_kw_count}")

        # Tổng hợp các từ khóa
        all_keywords = []
        for kw_list in df_keywords["keywords"].astype(str):
            keywords = [k.strip().lower() for k in kw_list.split(",") if k.strip()]
            all_keywords.extend(keywords)

        # Đếm tần suất từ khóa
        keyword_freq = Counter(all_keywords)

        print(f"\nTổng số từ khóa duy nhất: {len(keyword_freq)}")
        print(f"Top 15 từ khóa phổ biến nhất:")

        for i, (kw, count) in enumerate(keyword_freq.most_common(15), 1):
            coverage = count / len(df_keywords) * 100
            print(f"{i}. {kw}: {count} ({coverage:.2f}% độ phủ)")

        print("\nGiải thích: Phân tích từ khóa giúp đánh giá khả năng tìm kiếm của dữ liệu.")
        print("Ứng dụng cho tìm kiếm:")
        print("  - Chọn từ khóa phổ biến làm gợi ý tìm kiếm")
        print("  - Xây dựng từ điển đồng nghĩa cho các từ khóa phổ biến")
        print("  - Đánh trọng số cho từ khóa dựa trên mức độ phổ biến")

        # Vẽ biểu đồ phân phối số lượng từ khóa
        plt.figure(figsize=(12, 6))

        # Plot 1: Phân phối số lượng từ khóa
        plt.subplot(1, 2, 1)
        sns.histplot(df_keywords["keyword_count"], bins=min(20, max_kw_count), kde=True, color="green")
        plt.axvline(x=avg_kw_count, color='red', linestyle='--', label=f'Trung bình: {avg_kw_count:.2f}')
        plt.xlabel("Số lượng từ khóa")
        plt.ylabel("Số bản ghi")
        plt.title("Phân phối số lượng từ khóa mỗi bản ghi")
        plt.legend()

        # Plot 2: Top từ khóa phổ biến
        plt.subplot(1, 2, 2)
        top_kw = [kw for kw, _ in keyword_freq.most_common(10)]
        top_kw_counts = [keyword_freq[kw] for kw in top_kw]

        bars = plt.barh(range(len(top_kw)), top_kw_counts, color="teal")
        plt.yticks(range(len(top_kw)), top_kw)
        plt.xlabel("Tần suất")
        plt.title("Top 10 từ khóa phổ biến nhất")

        # Thêm giá trị vào thanh ngang
        for i, count in enumerate(top_kw_counts):
            plt.text(count + 0.5, i, str(count), va='center')

        plt.tight_layout()
        plt.show()

def run_analysis(file_path):
    """Chạy toàn bộ quá trình phân tích"""
    df = load_data(file_path)

    print("\n=========================================================")
    print("HƯỚNG DẪN ỨNG DỤNG PHÂN TÍCH DỮ LIỆU CHO TÌM KIẾM")
    print("=========================================================")
    print("Phân tích dữ liệu là bước quan trọng để tối ưu hóa hệ thống tìm kiếm, giúp:")
    print("1. Hiểu đặc điểm dữ liệu để cải thiện thuật toán xếp hạng")
    print("2. Xác định từ khóa quan trọng cho tìm kiếm từ khóa (keyword search)")
    print("3. Hiểu mối quan hệ ngữ nghĩa giữa các văn bản cho tìm kiếm ngữ nghĩa (semantic search)")
    print("=========================================================")

    # Chạy các phân tích
    category_distribution(df)
    analyze_title_length(df)
    word_frequency_analysis(df)
    analyze_ngrams(df, n=2, top_n=20)
    analyze_ngrams(df, n=3, top_n=15)
    analyze_keyword_co_occurrence(df, top_n=30, min_edge_weight=2)
    extract_named_entities(df, sample_size=500)
    analyze_semantic_similarity(df, sample_size=1000)
    analyze_search_keywords_quality(df)

    print("\n=========================================================")
    print("TÓM TẮT & HƯỚNG DẪN ỨNG DỤNG")
    print("=========================================================")
    print("Dựa trên phân tích trên, một số đề xuất cho hệ thống tìm kiếm:")

    print("\n1. Cho tìm kiếm từ khóa (keyword search):")
    print("   - Ưu tiên các từ có tần suất trung bình, loại bỏ stopwords")
    print("   - Sử dụng n-grams phổ biến làm từ điển gợi ý tìm kiếm")
    print("   - Đánh trọng số cao hơn cho các thực thể có tên (tên người, tổ chức, địa điểm)")
    print("   - Cân nhắc stemming/lemmatization để khớp các dạng khác nhau của cùng một từ")

    print("\n2. Cho tìm kiếm ngữ nghĩa (semantic search):")
    print("   - Sử dụng các mô hình nhúng từ (word embeddings) làm cơ sở tìm kiếm ngữ nghĩa")
    print("   - Khai thác thông tin từ đồ thị đồng xuất hiện để mở rộng truy vấn")
    print("   - Nhóm các văn bản tương tự để đa dạng hóa kết quả tìm kiếm")
    print("   - Kết hợp thông tin từ ngữ cảnh toàn văn bản, không chỉ từ các từ khóa riêng lẻ")

    print("\n3. Kết hợp cả hai phương pháp:")
    print("   - Sử dụng phương pháp tổng hợp kết quả (hybrid approach)")
    print("   - Điều chỉnh trọng số dựa trên độ dài tiêu đề và mức độ đặc thù của từ khóa")
    print("   - Cải thiện trải nghiệm người dùng bằng gợi ý tìm kiếm thông minh")
    print("   - Theo dõi và học từ hành vi người dùng để cải thiện thuật toán xếp hạng")

    print("\nLưu ý: Cần kiểm thử hiệu suất các phương pháp tìm kiếm trên tập dữ liệu cụ thể.")

# Chạy phân tích với file CSV
if __name__ == "__main__":
    run_analysis("WebScrapData_rows.csv")
