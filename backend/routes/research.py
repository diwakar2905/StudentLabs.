from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

class SearchQuery(BaseModel):
    topic: str

class SearchResult(BaseModel):
    paper_id: str
    title: str
    abstract: str
    authors: List[str]
    year: int

class SummarizeRequest(BaseModel):
    paper_id: str

@router.post("/search", response_model=List[SearchResult])
async def search_papers(query: SearchQuery):
    # Mock Semantic Scholar / arXiv API behavior
    return [
        {
            "paper_id": "arxiv:1234.5678",
            "title": f"Recent Advances in {query.topic}",
            "abstract": "This paper discusses the core methodologies and significant findings related to the topic...",
            "authors": ["John Doe", "Jane Smith"],
            "year": 2024
        },
        {
            "paper_id": "semantic:987654321",
            "title": f"A Comprehensive Review of {query.topic}",
            "abstract": "We present a thorough literature review of the subject matter, highlighting the latest trends...",
            "authors": ["Alice Johnson"],
            "year": 2023
        }
    ]

@router.post("/summarize")
async def summarize_paper(request: SummarizeRequest):
    # Mock extracting core methodology/findings
    return {
        "paper_id": request.paper_id,
        "summary": "The methodology involves a novel approach to the problem, yielding a 20% improvement in accuracy. Key findings suggest that existing frameworks can be adapted effectively."
    }
