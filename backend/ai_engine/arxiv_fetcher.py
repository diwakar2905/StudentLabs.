"""
arXiv Paper Fetcher - Retrieves real research papers from arXiv

This module connects to arXiv's free API to fetch academic papers
based on research topic queries. No authentication required.
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


def fetch_arxiv_papers(topic: str, max_results: int = 5) -> List[Dict]:
    """
    Fetch research papers from arXiv API based on topic query.
    
    Args:
        topic (str): Search query (e.g., "machine learning", "AI in healthcare")
        max_results (int): Maximum number of papers to return (default: 5, max: 100)
    
    Returns:
        List[Dict]: List of paper objects with keys:
            - paper_id: arXiv paper ID
            - title: Paper title
            - abstract: Paper abstract
            - authors: List of author names
            - year: Publication year (as integer)
            - url: Link to paper on arXiv
            - published: Full publication date (YYYY-MM-DD)
    
    Raises:
        requests.RequestException: If API request fails
        ET.ParseError: If XML parsing fails
    
    Example:
        >>> papers = fetch_arxiv_papers("machine learning", max_results=5)
        >>> print(papers[0]['title'])
        "Deep Learning Methods for Classification"
        >>> print(papers[0]['authors'])
        ['Smith, John', 'Chen, Wei', 'Li, Ming']
    """
    
    # Validate inputs
    if not topic or not isinstance(topic, str):
        logger.error(f"Invalid topic: {topic}")
        return []
    
    if max_results > 100:
        max_results = 100
        logger.warning("max_results capped at 100 (arXiv API limit)")
    
    try:
        # Build arXiv API query URL
        # search_query=all:{topic} searches in title, abstract, authors
        url = f"http://export.arxiv.org/api/query?search_query=all:{topic}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
        
        logger.info(f"Fetching papers from arXiv for topic: '{topic}'")
        
        # Fetch papers from arXiv
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise error for bad status codes
        
        # Parse XML response
        root = ET.fromstring(response.content)
        
        # Define namespaces used in arXiv API responses
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom'
        }
        
        papers = []
        
        # Extract each paper entry from XML
        for entry in root.findall('atom:entry', namespaces):
            try:
                # Extract title (remove line breaks for cleaner text)
                title_elem = entry.find('atom:title', namespaces)
                title = title_elem.text.strip() if title_elem is not None else "Unknown"
                
                # Extract abstract (remove line breaks)
                abstract_elem = entry.find('atom:summary', namespaces)
                abstract = abstract_elem.text.strip().replace('\n', ' ') if abstract_elem is not None else "No abstract"
                
                # Extract publication date
                published_elem = entry.find('atom:published', namespaces)
                published = published_elem.text if published_elem is not None else "Unknown"
                year = int(published[:4]) if published != "Unknown" else 2024
                
                # Extract paper ID and construct URL
                id_elem = entry.find('atom:id', namespaces)
                if id_elem is not None:
                    paper_id = id_elem.text.split('/abs/')[-1]  # Extract ID from URL
                    paper_url = f"https://arxiv.org/abs/{paper_id}"
                else:
                    continue  # Skip entries without ID
                
                # Extract authors
                authors = []
                for author_elem in entry.findall('atom:author', namespaces):
                    name_elem = author_elem.find('atom:name', namespaces)
                    if name_elem is not None:
                        authors.append(name_elem.text)
                
                # Ensure at least one author
                if not authors:
                    authors = ["Unknown Author"]
                
                # Create paper object
                paper = {
                    "paper_id": paper_id,
                    "title": title,
                    "abstract": abstract,
                    "authors": authors,
                    "year": year,
                    "url": paper_url,
                    "published": published,
                    "source": "arXiv"  # Track data source
                }
                
                papers.append(paper)
                logger.debug(f"Added paper: {title}")
                
            except Exception as e:
                logger.warning(f"Error processing paper entry: {e}")
                continue
        
        logger.info(f"Successfully fetched {len(papers)} papers")
        return papers
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch papers from arXiv: {e}")
        return []
    except ET.ParseError as e:
        logger.error(f"Failed to parse arXiv response: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in fetch_arxiv_papers: {e}")
        return []


def search_arxiv(query: str, max_results: int = 10) -> List[Dict]:
    """
    Advanced arXiv search with better formatting.
    
    Args:
        query (str): Search query
        max_results (int): Maximum results to return
    
    Returns:
        List[Dict]: Papers found on arXiv
    """
    return fetch_arxiv_papers(query, max_results)


def get_recent_papers(topic: str, max_results: int = 5, years_back: int = 3) -> List[Dict]:
    """
    Get recent papers published within last N years.
    
    Args:
        topic (str): Search topic
        max_results (int): Maximum papers to return
        years_back (int): How many years back to search (default: 3)
    
    Returns:
        List[Dict]: Recent papers matching topic
    """
    papers = fetch_arxiv_papers(topic, max_results)
    
    from datetime import datetime, timedelta
    cutoff_year = datetime.now().year - years_back
    
    recent = [p for p in papers if p['year'] >= cutoff_year]
    return recent


if __name__ == "__main__":
    # Example usage / testing
    logging.basicConfig(level=logging.INFO)
    
    print("🔍 Testing arXiv API Fetcher...")
    print()
    
    # Search for papers on a topic
    papers = fetch_arxiv_papers("machine learning classification", max_results=3)
    
    print(f"Found {len(papers)} papers:\n")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'][:2])}...")
        print(f"   Year: {paper['year']}")
        print(f"   URL: {paper['url']}")
        print(f"   Abstract: {paper['abstract'][:100]}...")
        print()
