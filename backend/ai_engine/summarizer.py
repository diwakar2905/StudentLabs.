"""
Paper Summarizer - Condenses research paper abstracts for better assignment quality

This module uses transformer models to summarize paper abstracts, improving
the quality and readability of generated assignments.

The summarizer can handle various text lengths and uses BART (Denoising Autoencoder
based on Transformer) which is excellent for abstractive summarization.
"""

import logging
from typing import Optional, List
import warnings

# Suppress transformers warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

# Initialize summarizer pipeline lazily (only when first used)
_summarizer = None


def _get_summarizer():
    """
    Initialize and return the summarizer pipeline.
    Uses lazy loading to avoid loading model until needed.
    
    This uses facebook/bart-large-cnn which is:
    - Trained on CNN/DailyMail dataset (news summarization)
    - 400M parameters
    - ~2GB disk space after download
    - Works well for academic abstracts
    
    Returns:
        transformers.pipeline: Initialized summarization pipeline
    """
    global _summarizer
    
    if _summarizer is None:
        try:
            logger.info("Loading BART summarizer model (first use)...")
            from transformers import pipeline
            
            # Load the summarization pipeline
            # This will download the model on first run (~2GB)
            _summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=-1  # -1 = CPU, 0+ = GPU device ID
            )
            logger.info("✅ Summarizer model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load summarizer: {e}")
            raise RuntimeError(f"Could not initialize summarizer: {e}")
    
    return _summarizer


def summarize_text(text: str, max_length: int = 150, min_length: int = 50) -> str:
    """
    Summarize text using BART transformer model.
    
    Args:
        text (str): Text to summarize
        max_length (int): Maximum summary length in tokens (default: 150)
        min_length (int): Minimum summary length in tokens (default: 50)
    
    Returns:
        str: Summarized text
    
    Example:
        >>> abstract = "This paper presents a novel deep learning approach..."
        >>> summary = summarize_text(abstract)
        >>> print(summary)
        "A novel deep learning method for classification tasks..."
    """
    
    # Validate input
    if not text or not isinstance(text, str):
        logger.warning("Invalid text input to summarizer")
        return text
    
    # If text is short enough, return as-is
    # Rough estimate: 1 token ≈ 4 characters
    if len(text) < 200:
        logger.debug("Text too short for summarization, returning as-is")
        return text.strip()
    
    try:
        summarizer = _get_summarizer()
        
        # Clean up text (remove extra whitespace)
        cleaned_text = " ".join(text.split())
        
        # Adjust parameters for text length
        # For very long abstracts, use longer max_length
        text_length = len(cleaned_text)
        if text_length > 1000:
            adjusted_max = 200
        else:
            adjusted_max = max_length
        
        # Run summarization
        logger.debug(f"Summarizing {text_length} chars to ~{adjusted_max} tokens")
        summary = summarizer(
            cleaned_text,
            max_length=adjusted_max,
            min_length=min_length,
            do_sample=False  # Greedy decoding for consistency
        )
        
        # Extract summary text from response
        summary_text = summary[0]['summary_text']
        
        logger.debug(f"Summary length: {len(summary_text)} chars")
        return summary_text
        
    except Exception as e:
        logger.error(f"Error summarizing text: {e}")
        # Fallback: return first 150 chars if summarization fails
        return text[:150] + "..." if len(text) > 150 else text


def summarize_abstract(abstract: str) -> str:
    """
    Specialized function for summarizing research paper abstracts.
    
    Paper abstracts are already fairly concise, so this does light summarization.
    
    Args:
        abstract (str): Paper abstract
    
    Returns:
        str: Condensed abstract for use in assignments
    
    Example:
        >>> abstract = "This comprehensive study examines..."
        >>> condensed = summarize_abstract(abstract)
    """
    
    if not abstract or len(abstract) < 100:
        return abstract
    
    # For abstracts, use smaller summary (they're already condensed)
    return summarize_text(
        abstract,
        max_length=100,  # Shorter than full text
        min_length=30
    )


def summarize_papers(papers: List[dict]) -> List[dict]:
    """
    Summarize abstracts for multiple papers at once.
    
    Useful for batch processing all papers in a project.
    
    Args:
        papers (List[dict]): List of paper dicts with 'abstract' key
    
    Returns:
        List[dict]: Papers with added 'abstract_summary' key
    
    Example:
        >>> papers = [
        ...     {"title": "Paper 1", "abstract": "Long abstract..."},
        ...     {"title": "Paper 2", "abstract": "Another abstract..."}
        ... ]
        >>> summarized = summarize_papers(papers)
        >>> print(summarized[0]['abstract_summary'])
    """
    logger.info(f"Summarizing abstracts for {len(papers)} papers...")
    
    summarized = []
    for i, paper in enumerate(papers, 1):
        try:
            paper_copy = paper.copy()
            if 'abstract' in paper:
                paper_copy['abstract_summary'] = summarize_abstract(paper['abstract'])
                summarized.append(paper_copy)
                logger.debug(f"({i}/{len(papers)}) Summarized: {paper['title'][:50]}...")
            else:
                summarized.append(paper_copy)
        except Exception as e:
            logger.warning(f"Failed to summarize paper {i}: {e}")
            summarized.append(paper)
    
    logger.info(f"✅ Summarization complete for {len(summarized)} papers")
    return summarized


def get_abstract_pair(paper: dict) -> tuple:
    """
    Get both original and summarized abstract for a paper.
    
    Useful for comparison or A/B testing.
    
    Args:
        paper (dict): Paper object with 'abstract' key
    
    Returns:
        tuple: (original_abstract, summarized_abstract)
    """
    original = paper.get('abstract', '')
    summarized = summarize_abstract(original)
    return (original, summarized)


# Quality metrics
def measure_compression_ratio(original: str, summarized: str) -> float:
    """
    Measure how much the text was compressed.
    
    Returns ratio like 0.33 (original was 3x longer).
    
    Args:
        original (str): Original text
        summarized (str): Summarized text
    
    Returns:
        float: Compression ratio (0-1)
    """
    if len(original) == 0:
        return 1.0
    
    ratio = len(summarized) / len(original)
    return round(ratio, 3)


if __name__ == "__main__":
    # Example usage / testing
    logging.basicConfig(level=logging.INFO)
    
    print("📝 Testing Paper Summarizer...")
    print()
    
    # Example abstract
    sample_abstract = """
    This paper presents a comprehensive study of deep learning approaches for medical image 
    analysis. We examine state-of-the-art convolutional neural networks and their applications 
    in pathology. Our analysis covers 50+ recent papers and demonstrates that transformer-based 
    models achieve superior performance on benchmark datasets. We also discuss the computational 
    complexity and practical deployment challenges. The results suggest that hybrid approaches 
    combining visual features with semantic understanding provide the best accuracy-efficiency 
    tradeoff for clinical applications. Future work will focus on interpretability and 
    generalization across diverse imaging modalities.
    """
    
    print("ORIGINAL ABSTRACT:")
    print(f"Length: {len(sample_abstract)} characters")
    print(sample_abstract)
    print()
    
    print("SUMMARIZED ABSTRACT:")
    summary = summarize_text(sample_abstract)
    print(f"Length: {len(summary)} characters")
    print(f"Compression: {measure_compression_ratio(sample_abstract, summary):.1%}")
    print(summary)
