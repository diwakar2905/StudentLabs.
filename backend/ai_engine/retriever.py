"""
Paper Retriever Module - FAISS-based Vector Search for RAG

This module implements Retrieval-Augmented Generation (RAG) for assignment building.
It indexes paper summaries and retrieves relevant content based on topic similarity.

Architecture:
1. Convert paper summaries to embeddings (using sentence-transformers)
2. Store embeddings in FAISS index
3. Retrieve top-K most relevant papers for any query
4. Return relevant summaries to feed to AI for context-aware generation

Persistence:
- FAISS indexes stored per-project in faiss_indexes/ directory
- Metadata stored in JSON files (project_id.json)
- Avoids recomputing embeddings for same papers
"""

import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Create faiss_indexes directory if it doesn't exist
FAISS_INDEXES_DIR = Path("faiss_indexes")
FAISS_INDEXES_DIR.mkdir(exist_ok=True)

# Cached index and embedder (in-memory cache)
_faiss_index = None
_embeddings_model = None
_indexed_papers = None
_paper_metadata = None
_current_project_id = None


def _get_embeddings_model():
    """
    Lazy load the sentence embedding model.
    Uses 'all-MiniLM-L6-v2' which is:
    - Fast (384 dimensions)
    - Good quality
    - ~80MB on disk
    
    Returns:
        sentence_transformers.SentenceTransformer: Embedding model
    """
    global _embeddings_model
    
    if _embeddings_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info("Loading embeddings model (first use only)...")
            _embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Embeddings model loaded")
            
        except ImportError:
            logger.error("sentence-transformers not installed")
            raise RuntimeError("Install with: pip install sentence-transformers")
    
    return _embeddings_model


def _get_faiss_index():
    """
    Get or create FAISS index.
    
    Returns:
        faiss.IndexFlatL2: FAISS index for similarity search
    """
    global _faiss_index
    
    if _faiss_index is None:
        try:
            import faiss
            
            # Create flat index (exact search, no approximation)
            # L2 distance metric
            dimension = 384  # all-MiniLM-L6-v2 output dimension
            _faiss_index = faiss.IndexFlatL2(dimension)
            logger.debug("FAISS index created")
            
        except ImportError:
            logger.error("faiss not installed")
            raise RuntimeError("Install with: pip install faiss-cpu (or faiss-gpu)")
    
    return _faiss_index


def _get_index_paths(project_id: int) -> Tuple[Path, Path]:
    """
    Get file paths for FAISS index and metadata for a project.
    
    Args:
        project_id (int): Project ID
    
    Returns:
        Tuple[Path, Path]: (index_path, metadata_path)
    """
    index_path = FAISS_INDEXES_DIR / f"project_{project_id}.index"
    metadata_path = FAISS_INDEXES_DIR / f"project_{project_id}.json"
    return index_path, metadata_path


def save_index(project_id: int) -> bool:
    """
    Persist FAISS index and metadata to disk.
    
    Saves the current in-memory FAISS index to disk for the given project.
    This is crucial for performance - allows reusing embeddings without recomputation.
    
    Args:
        project_id (int): Project ID to save index for
    
    Returns:
        bool: True if successful, False otherwise
    
    Example:
        >>> index_papers(papers)
        >>> success = save_index(project_id=123)
        >>> print(f"Saved: {success}")
    """
    global _faiss_index, _indexed_papers, _paper_metadata, _current_project_id
    
    if _faiss_index is None or _indexed_papers is None:
        logger.warning("No index to save")
        return False
    
    try:
        import faiss
        
        index_path, metadata_path = _get_index_paths(project_id)
        
        # Save FAISS index
        faiss.write_index(_faiss_index, str(index_path))
        logger.debug(f"✅ Saved FAISS index to {index_path}")
        
        # Save metadata as JSON
        with open(metadata_path, 'w') as f:
            json.dump({
                'papers': _indexed_papers,
                'metadata': _paper_metadata,
                'project_id': project_id
            }, f, indent=2, default=str)
        logger.debug(f"✅ Saved metadata to {metadata_path}")
        
        _current_project_id = project_id
        logger.info(f"✅ Project {project_id} index persisted to disk")
        return True
        
    except Exception as e:
        logger.error(f"Error saving index: {e}")
        return False


def load_index(project_id: int) -> bool:
    """
    Load persisted FAISS index and metadata from disk.
    
    Loads a previously saved index for a project. Avoids expensive re-embedding.
    Major performance improvement for projects with many papers.
    
    Args:
        project_id (int): Project ID to load index for
    
    Returns:
        bool: True if loaded successfully, False if not found or error
    
    Example:
        >>> success = load_index(project_id=123)
        >>> if success:
        ...     results = retrieve_relevant_content("query")
        ...     print(f"Found {len(results)} relevant papers")
    """
    global _faiss_index, _indexed_papers, _paper_metadata, _current_project_id
    
    try:
        import faiss
        
        index_path, metadata_path = _get_index_paths(project_id)
        
        # Check if files exist
        if not index_path.exists() or not metadata_path.exists():
            logger.debug(f"Index not found for project {project_id}")
            return False
        
        # Load FAISS index
        _faiss_index = faiss.read_index(str(index_path))
        logger.debug(f"✅ Loaded FAISS index from {index_path}")
        
        # Load metadata
        with open(metadata_path, 'r') as f:
            data = json.load(f)
            _indexed_papers = data.get('papers', [])
            _paper_metadata = data.get('metadata', {})
        logger.debug(f"✅ Loaded metadata from {metadata_path}")
        
        _current_project_id = project_id
        logger.info(f"✅ Project {project_id} index loaded from disk ({len(_indexed_papers)} papers)")
        return True
        
    except Exception as e:
        logger.error(f"Error loading index: {e}")
        return False


def index_papers(papers: List[Dict], project_id: int = None, save_to_disk: bool = True) -> int:
    """
    Index paper summaries for retrieval.
    
    This creates vector embeddings from paper abstracts and stores them
    in a FAISS index for fast similarity search.
    
    Args:
        papers (List[Dict]): List of papers with keys:
            - paper_id or id: Unique identifier
            - title: Paper title
            - abstract: Paper abstract
            - authors: Author names
            - year: Publication year
        project_id (int): Project ID (optional, used for persistence)
        save_to_disk (bool): Auto-save index to disk after indexing (default: True)
    
    Returns:
        int: Number of papers indexed
    
    Example:
        >>> papers = fetch_arxiv_papers("machine learning", max_results=5)
        >>> num_indexed = index_papers(papers, project_id=123)
        >>> print(f"Indexed {num_indexed} papers")
    """
    
    if not papers:
        logger.warning("No papers provided to index")
        return 0
    
    try:
        logger.info(f"Indexing {len(papers)} papers..." + (f" for project {project_id}" if project_id else ""))
        
        # Store global references
        global _indexed_papers, _paper_metadata
        _indexed_papers = papers
        _paper_metadata = {}
        
        # Get embeddings model
        embedder = _get_embeddings_model()
        
        # Get FAISS index
        index = _get_faiss_index()
        
        # Clear existing index if it has data
        if index.ntotal > 0:
            import faiss
            index.reset()
        
        # Prepare texts to embed
        texts_to_embed = []
        for i, paper in enumerate(papers):
            # Use paper abstract for embedding
            abstract = paper.get('abstract', '')
            if not abstract:
                abstract = paper.get('title', '')
            
            if abstract:
                texts_to_embed.append(abstract)
            else:
                texts_to_embed.append(f"No abstract provided for {paper.get('title', 'Unknown')}")
        
        logger.debug(f"Embedding {len(texts_to_embed)} paper abstracts...")
        
        # Generate embeddings
        embeddings = embedder.encode(texts_to_embed, convert_to_numpy=True)
        
        # Add to FAISS index
        embeddings = np.asarray(embeddings, dtype=np.float32)
        index.add(embeddings)
        
        # Store metadata for later retrieval
        for i, paper in enumerate(papers):
            paper_id = paper.get('paper_id') or paper.get('id')
            _paper_metadata[i] = {
                'id': paper_id,
                'title': paper.get('title', 'Unknown'),
                'authors': paper.get('authors', 'Unknown'),
                'year': paper.get('year', 0),
                'abstract': paper.get('abstract', ''),
                'url': paper.get('url', ''),
                'index_position': i
            }
        
        logger.info(f"✅ Successfully indexed {len(papers)} papers ({len(embeddings)} embeddings)")
        
        # Persist to disk if project_id provided and save_to_disk is True
        if project_id and save_to_disk:
            save_index(project_id)
        
        return len(papers)
        
    except Exception as e:
        logger.error(f"Error indexing papers: {e}")
        raise


def retrieve_relevant_content(
    query: str,
    top_k: int = 3,
    threshold: float = 0.0,
    project_id: int = None
) -> List[str]:
    """
    Retrieve relevant paper summaries for a query.
    
    Uses FAISS to find the most similar papers to the query topic.
    Returns the abstracts/summaries for use as context in AI generation.
    
    If project_id is provided and index not in memory, loads from disk.
    This enables fast retrieval across sessions without re-embedding.
    
    Args:
        query (str): Search query (topic or question)
        top_k (int): Number of relevant papers to retrieve (default: 3)
        threshold (float): Similarity threshold (lower = more similar, default: no threshold)
        project_id (int): Project ID (optional, loads from disk if needed)
    
    Returns:
        List[str]: Relevant paper abstracts/summaries
    
    Example:
        >>> relevant = retrieve_relevant_content("machine learning healthcare", top_k=3, project_id=123)
        >>> print(f"Found {len(relevant)} relevant papers:")
        >>> for content in relevant:
        ...     print(f"- {content[:100]}...")
    """
    
    if not query:
        logger.warning("Empty query provided")
        return []
    
    # If index not in memory but project_id provided, try to load from disk
    if (_indexed_papers is None or len(_indexed_papers) == 0) and project_id:
        logger.debug(f"Loading index from disk for project {project_id}...")
        if not load_index(project_id):
            logger.warning(f"Could not load index for project {project_id}")
            return []
    
    if _indexed_papers is None or len(_indexed_papers) == 0:
        logger.warning("No papers indexed. Call index_papers() first.")
        return []
    
    try:
        logger.debug(f"Retrieving content for query: '{query}'")
        
        # Get embeddings model
        embedder = _get_embeddings_model()
        
        # Get FAISS index
        index = _get_faiss_index()
        
        # Embed the query
        query_embedding = embedder.encode([query], convert_to_numpy=True)
        query_embedding = np.asarray(query_embedding, dtype=np.float32)
        
        # Search FAISS index
        distances, indices = index.search(query_embedding, top_k)
        
        logger.debug(f"Found {len(indices[0])} results with distances: {distances[0]}")
        
        # Extract relevant content
        relevant_content = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < 0 or idx >= len(_indexed_papers):
                continue
            
            paper = _indexed_papers[int(idx)]
            
            # Format content for including in AI prompt
            content = f"""
Paper: {paper.get('title', 'Unknown')}
Authors: {paper.get('authors', 'Unknown')}
Year: {paper.get('year', 'N/A')}

Abstract: {paper.get('abstract', 'No abstract available')}
"""
            relevant_content.append(content.strip())
        
        logger.info(f"✅ Retrieved {len(relevant_content)} relevant papers for RAG context")
        return relevant_content
        
    except Exception as e:
        logger.error(f"Error retrieving content: {e}")
        return []


def get_paper_metadata(paper_id: str) -> Optional[Dict]:
    """
    Get metadata for a specific paper by ID.
    
    Args:
        paper_id (str): Paper ID to look up
    
    Returns:
        Dict: Paper metadata or None if not found
    """
    if _paper_metadata is None:
        return None
    
    for metadata in _paper_metadata.values():
        if metadata.get('id') == paper_id:
            return metadata
    
    return None


def get_indexed_paper_count() -> int:
    """
    Get the number of currently indexed papers.
    
    Returns:
        int: Number of indexed papers
    """
    if _indexed_papers is None:
        return 0
    return len(_indexed_papers)


def clear_index():
    """
    Clear the FAISS index and reset all data.
    
    Useful for resetting before indexing new papers.
    """
    global _faiss_index, _indexed_papers, _paper_metadata
    
    if _faiss_index is not None:
        _faiss_index.reset()
    
    _indexed_papers = None
    _paper_metadata = None
    
    logger.info("FAISS index cleared")


def build_retrieval_context(papers: List[Dict], query: str = None, project_id: int = None) -> str:
    """
    Build a complete retrieval context for AI generation.
    
    Orchestrates indexing and retrieval to create prompt context.
    Caches results per project for efficiency.
    
    Args:
        papers (List[Dict]): Papers to index and search
        query (str): Query to search for (if None, uses general query)
        project_id (int): Project ID for caching (optional)
    
    Returns:
        str: Formatted context for AI prompts
    """
    
    if not papers:
        logger.warning("No papers provided for retrieval context")
        return ""
    
    try:
        # Index the papers (will auto-save if project_id provided)
        index_papers(papers, project_id=project_id, save_to_disk=bool(project_id))
        
        # If no query provided, use general context
        if not query:
            query = "main topic and key findings"
        
        # Retrieve relevant content
        relevant_content = retrieve_relevant_content(query, top_k=min(5, len(papers)), project_id=project_id)
        
        # Format as context
        context = "# Research Context\n\n"
        context += f"Retrieved {len(relevant_content)} relevant papers:\n\n"
        context += "\n---\n\n".join(relevant_content)
        
        return context
        
    except Exception as e:
        logger.error(f"Error building retrieval context: {e}")
        return ""


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    print("🔍 Testing Paper Retriever (FAISS RAG)...")
    print()
    
    # Mock papers for testing
    test_papers = [
        {
            "paper_id": "1001",
            "title": "Deep Learning for Medical Imaging",
            "authors": "Smith et al.",
            "year": 2024,
            "abstract": "This paper discusses deep learning applications in medical imaging analysis."
        },
        {
            "paper_id": "1002",
            "title": "Transformer Models in Healthcare",
            "authors": "Chen et al.",
            "year": 2024,
            "abstract": "Transformers have revolutionized natural language processing in healthcare documentation."
        },
        {
            "paper_id": "1003",
            "title": "Computer Vision for Pathology",
            "authors": "Patel et al.",
            "year": 2023,
            "abstract": "This work explores computer vision techniques for automated pathology analysis."
        }
    ]
    
    print("📚 Indexing test papers...")
    num_indexed = index_papers(test_papers)
    print(f"✅ Indexed {num_indexed} papers\n")
    
    # Test retrieval
    query = "medical imaging and deep learning"
    print(f"🔎 Retrieving papers for query: '{query}'")
    results = retrieve_relevant_content(query, top_k=2)
    
    print(f"\n✅ Found {len(results)} relevant papers:")
    for i, content in enumerate(results, 1):
        print(f"\n{i}. {content[:200]}...")
