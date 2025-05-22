import os
import re
import pandas as pd
import numpy as np
import torch
from sentence_transformers import SentenceTransformer, util
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Map of all categories
CATEGORY_MAP = {
    'ARTS': 0, 'ARTS & CULTURE': 1, 'BLACK VOICES': 2, 'BUSINESS': 3, 
    'COLLEGE': 4, 'COMEDY': 5, 'CRIME': 6, 'CULTURE & ARTS': 7, 
    'DIVORCE': 8, 'EDUCATION': 9, 'ENTERTAINMENT': 10, 'ENVIRONMENT': 11, 
    'FIFTY': 12, 'FOOD & DRINK': 13, 'GOOD NEWS': 14, 'GREEN': 15, 
    'HEALTHY LIVING': 16, 'HOME & LIVING': 17, 'IMPACT': 18, 'LATINO VOICES': 19, 
    'MEDIA': 20, 'MONEY': 21, 'PARENTING': 22, 'PARENTS': 23, 
    'POLITICS': 24, 'QUEER VOICES': 25, 'RELIGION': 26, 'SCIENCE': 27, 
    'SPORTS': 28, 'STYLE': 29, 'STYLE & BEAUTY': 30, 'TASTE': 31, 
    'TECH': 32, 'THE WORLDPOST': 33, 'TRAVEL': 34, 'U.S. NEWS': 35, 
    'WEDDINGS': 36, 'WEIRD NEWS': 37, 'WELLNESS': 38, 'WOMEN': 39, 
    'WORLD NEWS': 40, 'WORLDPOST': 41
}
# Reverse mapping for readability
CATEGORY_NAMES = {v: k for k, v in CATEGORY_MAP.items()}

def load_corpus_embeddings_from_csv(csv_path, sample_size=None):
    """
    Load article data and their embeddings from a CSV file
    
    Args:
        csv_path (str): Path to the CSV file
        sample_size (int, optional): Number of samples to load (useful for testing)
        
    Returns:
        Tuple: (corpus_embeddings tensor, corpus_ids list)
    """
    logger.info(f"Loading data from {csv_path}")
    
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Take a sample if specified
    if sample_size and sample_size < len(df):
        df = df.sample(sample_size, random_state=42)
    
    logger.info(f"Loaded {len(df)} articles")
    
    # Check if the 'vector' column exists
    if 'vector' in df.columns:
        # Extract vectors
        try:
            # First display a sample vector for debugging
            sample_vec = df['vector'].iloc[0]
            logger.info(f"Sample vector format: {sample_vec[:100]}...")
            
            # Parse vectors efficiently
            # This regex extracts all float values from the string, handling np.float32() format
            vectors = df['vector'].apply(lambda x: 
                np.array([float(val) for val in re.findall(r'-?\d+\.\d+', x)], 
                         dtype=np.float32)).tolist()
            
            # Convert to tensor for efficient processing
            corpus_embeddings = torch.tensor(vectors)
            
            # Create IDs from the dataframe index
            corpus_ids = df.index.tolist()
            
            logger.info(f"Successfully loaded {len(vectors)} embeddings with dimension {len(vectors[0])}")
            return corpus_embeddings, corpus_ids
        
        except Exception as e:
            logger.error(f"Error parsing vectors: {e}")
            raise
    else:
        logger.error("No 'vector' column found in the CSV file")
        raise ValueError("No 'vector' column found in the CSV file")

def load_article_data(csv_path):
    """
    Load article data from a CSV file
    
    Args:
        csv_path (str): Path to the CSV file
        
    Returns:
        DataFrame: Article data
    """
    return pd.read_csv(csv_path)

def semantic_search(query, model, corpus_embeddings, corpus_ids, article_data, top_k=5):
    """
    Perform semantic search on the corpus
    
    Args:
        query (str): Query text
        model (SentenceTransformer): Model to encode the query
        corpus_embeddings (Tensor): Corpus embeddings
        corpus_ids (list): Corpus IDs
        article_data (DataFrame): Article data
        top_k (int): Number of top results to return
        
    Returns:
        DataFrame: Top matching articles
    """
    # Encode the query
    query_embedding = model.encode(query, convert_to_tensor=True)
    
    # Perform semantic search using optimized function from sentence_transformers
    hits = util.semantic_search(
        query_embedding, 
        corpus_embeddings, 
        query_chunk_size=1,  # Single query
        corpus_chunk_size=corpus_embeddings.shape[0],  # Process all at once if it fits in memory
        top_k=top_k
    )
    
    # Get the top matches
    top_hits = hits[0]  # hits is a list of lists, get the first list (only one query)
    
    # Collect the results
    results = []
    for hit in top_hits:
        corpus_id = corpus_ids[hit['corpus_id']]
        article = article_data.iloc[corpus_id]
        results.append({
            'score': hit['score'],
            'headline': article['headline'],
            'category': article['category'],
            'short_description': article['short_description']
        })
    
    return pd.DataFrame(results)

def test_semantic_search_returns_relevant_results():
    """Test that semantic search returns relevant results"""
    # Paths
    csv_path = "data/analysis/WebScrapData_rows.csv"
    
    # Check if the file exists
    if not os.path.exists(csv_path):
        logger.error(f"File not found: {csv_path}")
        return
    
    # Load corpus embeddings
    try:
        corpus_embeddings, corpus_ids = load_corpus_embeddings_from_csv(csv_path, sample_size=1000)
    except Exception as e:
        logger.error(f"Failed to load corpus embeddings: {e}")
        return
    
    # Load article data
    article_data = load_article_data(csv_path)
    
    # Load model
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, lightweight model
    
    # Test queries
    test_queries = [
        "Republicans and Democrats political differences",
        "Transgender bathroom laws and sexual assault",
        "Health and wellness tips",
        "Travel destinations"
    ]
    
    for query in test_queries:
        logger.info(f"Testing query: {query}")
        results = semantic_search(query, model, corpus_embeddings, corpus_ids, article_data)
        
        if len(results) > 0:
            logger.info(f"Top result: {results.iloc[0]['headline']} (Score: {results.iloc[0]['score']:.4f})")
            logger.info(f"Category: {results.iloc[0]['category']}")
            logger.info(f"Description: {results.iloc[0]['short_description']}")
        else:
            logger.warning("No results found")
        
        logger.info("-" * 80)
    
    logger.info("Semantic search test completed")

if __name__ == "__main__":
    test_semantic_search_returns_relevant_results()
