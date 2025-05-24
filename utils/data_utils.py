import pandas as pd
import numpy as np
import re
import torch
import logging
from typing import Tuple, List, Optional
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_news_data(csv_path: str, sample_size: Optional[int] = None) -> pd.DataFrame:
    """
    Load news article data from a CSV file
    
    Args:
        csv_path (str): Path to the CSV file
        sample_size (int, optional): Number of samples to load
        
    Returns:
        DataFrame: News article data
    """
    logger.info(f"Loading news data from {csv_path}")
    df = pd.read_csv(csv_path)
    
    if sample_size and sample_size < len(df):
        df = df.sample(sample_size, random_state=42)
    
    logger.info(f"Loaded {len(df)} news articles")
    return df

def parse_vector(vec_str: str) -> List[float]:
    """
    Parse vector string into a list of floats
    
    Args:
        vec_str (str): Vector string to parse
        
    Returns:
        List[float]: Vector as list of floats
    """
    try:
        # Extract all float values using regex
        return [float(val) for val in re.findall(r'-?\d+\.\d+', vec_str)]
    except Exception as e:
        logger.error(f"Error parsing vector: {e}")
        raise ValueError(f"Failed to parse vector: {e}")

def generate_embeddings(texts: List[str], model_name: str = 'all-MiniLM-L6-v2') -> torch.Tensor:
    """
    Generate embeddings for a list of texts
    
    Args:
        texts (List[str]): List of texts to encode
        model_name (str): Name of the SentenceTransformer model to use
        
    Returns:
        torch.Tensor: Tensor of embeddings
    """
    logger.info(f"Generating embeddings using {model_name}")
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, convert_to_tensor=True)
    logger.info(f"Generated {len(embeddings)} embeddings with dimension {embeddings.shape[1]}")
    return embeddings

def save_embeddings_to_csv(df: pd.DataFrame, embeddings: torch.Tensor, output_path: str):
    """
    Save embeddings to a CSV file
    
    Args:
        df (DataFrame): DataFrame with article data
        embeddings (torch.Tensor): Tensor of embeddings
        output_path (str): Path to save the CSV file
    """
    # Convert tensor to list of lists
    embeddings_list = embeddings.cpu().numpy().tolist()
    
    # Add embeddings to the DataFrame
    df['vector'] = embeddings_list
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    logger.info(f"Saved {len(df)} articles with embeddings to {output_path}")
