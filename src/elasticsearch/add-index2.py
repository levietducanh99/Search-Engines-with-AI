import os
import sys
import re
import logging
import psycopg2
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.qparser import MultifieldParser, OrGroup, PhrasePlugin
from whoosh.analysis import StemmingAnalyzer
from concurrent.futures import ProcessPoolExecutor
import spacy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database config
DB_CONFIG = {
    "host": "dpg-d0g2d1idbo4c73auv9i0-a.singapore-postgres.render.com",
    "port": "5432",
    "user": "hybrid_search_database_user",
    "password": "EvaQhGOaGF7QgdgteoxWvmfKvWe0VqM1",
    "database": "hybrid_search_database"
}

# Whoosh settings
INDEX_DIR = "whoosh_index"

# Schema
schema = Schema(
    id=ID(stored=True, unique=True),
    link=TEXT(stored=True),
    headline=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    category=KEYWORD(stored=True, commas=True),
    short_description=TEXT(stored=True),
    keywords_proper_nouns=TEXT(stored=True)
)

# Regex compile sẵn
clean_re = re.compile(r"<[^>]+>|[^a-z0-9\s]+")
multi_space_re = re.compile(r"\s+")
STOP_WORDS = set([
    "a", "an", "and", "the", "is", "are", "in", "on", "at", "for", "to", "with",
    "of", "by", "as", "from", "that", "this", "it", "be", "was", "were", "has", "have", "had",
    "but", "or", "if", "then", "else", "when", "while", "about", "can", "will", "just", "not"
])

def clean_text_fast(text):
    if not text:
        return ""
    text = text.lower()
    text = clean_re.sub(" ", text)
    text = multi_space_re.sub(" ", text).strip()
    return " ".join(w for w in text.split(" ") if w and w not in STOP_WORDS)

def process_row(row):
    return {
        "id": str(row[0]),
        "link": row[1] or "",
        "headline": clean_text_fast(row[2] or ""),
        "category": row[3] or "",
        "short_description": clean_text_fast(row[4] or ""),
        "keywords_proper_nouns": clean_text_fast(row[5] or "")
    }

def get_index():
    try:
        if not os.path.exists(INDEX_DIR):
            os.makedirs(INDEX_DIR)
            ix = create_in(INDEX_DIR, schema)
            logger.info(f"Created new index directory: {INDEX_DIR}")
            return ix, True
        elif not exists_in(INDEX_DIR):
            ix = create_in(INDEX_DIR, schema)
            logger.info(f"Created new index in existing directory: {INDEX_DIR}")
            return ix, True
        else:
            ix = open_dir(INDEX_DIR)
            logger.info(f"ℹ Using existing index with {ix.doc_count()} documents")
            return ix, False
    except Exception as e:
        logger.error(f"Error accessing index: {e}")
        sys.exit(1)

def connect_to_database():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Connected to PostgreSQL database")
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def fetch_documents_from_db():
    """Fetch and clean all documents from the database in parallel"""
    try:
        conn = connect_to_database()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, link, headline, category, short_description, keywords_proper_nouns
                FROM "WebScrapData_rows"
            """)
            rows = cursor.fetchall()
        conn.close()

        logger.info(f"Retrieved {len(rows)} rows. Cleaning in parallel...")

        with ProcessPoolExecutor(max_workers=6) as executor:
            documents = list(executor.map(process_row, rows))

        logger.info(f"Finished processing {len(documents)} documents")
        return documents
    except Exception as e:
        logger.error(f"Error fetching documents: {e}")
        sys.exit(1)

def index_documents(ix, documents):
    if not documents:
        logger.info("ℹ️ No documents to index")
        return
    try:
        writer = ix.writer()
        success = 0
        failed = 0
        for doc in documents:
            try:
                writer.update_document(
                    id=doc["id"],
                    link=doc["link"],
                    headline=doc["headline"],
                    category=doc["category"],
                    short_description=doc["short_description"],
                    keywords_proper_nouns=doc["keywords_proper_nouns"]
                )
                success += 1
            except Exception as e:
                failed += 1
                logger.warning(f"⚠️ Failed to index id={doc['id']}: {e}")
        writer.commit()
        logger.info(f"Indexed {success} documents. Failed: {failed}")
    except Exception as e:
        logger.error(f"Error indexing documents: {e}")

def load_spacy_model():
    try:
        return spacy.load("en_core_web_md")
    except OSError:
        logger.info("⏳ Downloading spaCy model...")
        import subprocess
        subprocess.call(["python", "-m", "spacy", "download", "en_core_web_md"])
        return spacy.load("en_core_web_md")

def detect_entities(nlp, query):
    doc = nlp(query)
    entities = set()
    for ent in doc.ents:
        if ent.label_ in ("PERSON", "ORG", "GPE", "PRODUCT"):
            entities.add(ent.text.lower())
    return entities

def search_documents(query, size=5):
    ix = open_dir(INDEX_DIR)
    with ix.searcher() as searcher:
        parser = MultifieldParser(
            ["headline^3", "category", "short_description", "keywords_proper_nouns^2"],
            schema=ix.schema,
            group=OrGroup
        )
        parser.remove_plugin_class(PhrasePlugin)
        parser.add_plugin(PhrasePlugin())

        q = parser.parse(f'"{query}"')
        results = searcher.search(q, limit=size)

        if not results:
            print("No results found.")
            return

        seen_ids = set()
        print(f"Found {len(results)} results for '{query}':")
        for i, hit in enumerate(results, 1):
            if hit["id"] in seen_ids:
                continue
            seen_ids.add(hit["id"])
            print("=" * 100)
            print(f"[{i}] ID: {hit['id']}")
            print(f"Headline: {hit['headline']}")
            print(f"Category: {hit['category']}")
            print(f"Short description: {hit['short_description']}")
            print(f"Keywords Proper Nouns: {hit['keywords_proper_nouns']}")
            print(f"Score: {hit.score}")
            print()

def export_index_info():
    ix = open_dir(INDEX_DIR)
    with open("index_info.txt", "w") as f:
        f.write("Whoosh Index Information\n")
        f.write("=====================\n\n")
        f.write(f"Index Location: {INDEX_DIR}\n")
        f.write(f"Number of Documents: {ix.doc_count()}\n\n")
        f.write("Schema:\n")
        for field_name, field_type in ix.schema.items():
            f.write(f"  - {field_name}: {field_type.__class__.__name__}\n")
    logger.info("Exported index information to index_info.txt")

# MAIN
if __name__ == "__main__":
    ix, is_new_index = get_index()

    if is_new_index:
        logger.info("Creating new index...")
        documents = fetch_documents_from_db()
        index_documents(ix, documents)
        export_index_info()
    else:
        logger.info("Using existing index")

    print("\n🔍 Search the document database")
    print("============================")
    while True:
        query = input("\nEnter search query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        search_documents(query)
