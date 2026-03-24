"""
AI Text Generator Module

Generates academic text sections using transformer models.
Supports context-based generation for research-backed content.

Architecture:
- Load Mistral-7B (instruction-tuned model) once on module import
- Provide context from research papers to ensure relevance
- Generate sections: abstract, introduction, discussion, conclusion
"""

from transformers import pipeline
from typing import List, Dict, Optional

# Load text generation model once (cached on first import)
_generator_cache = None

def _get_generator():
    """
    Lazy-load the text generation pipeline.
    Caches the generator to avoid reloading on each call.
    """
    global _generator_cache
    
    if _generator_cache is None:
        print("🚀 Loading Mistral-7B model (first time only, ~2-3 minutes)...")
        _generator_cache = pipeline(
            "text-generation",
            model="mistralai/Mistral-7B-Instruct",
            max_new_tokens=500,
            device=-1  # Use CPU (set to 0 for GPU if available)
        )
        print("✅ Model loaded successfully!")
    
    return _generator_cache


def generate_text(prompt: str, max_tokens: int = 500) -> str:
    """
    Generate text from a given prompt using Mistral model.
    
    Args:
        prompt: The prompt to generate from
        max_tokens: Maximum tokens to generate
    
    Returns:
        Generated text string
    """
    generator = _get_generator()
    
    try:
        result = generator(prompt, max_new_tokens=max_tokens)
        generated = result[0]["generated_text"]
        
        # Remove the original prompt from the output
        if prompt in generated:
            generated = generated.replace(prompt, "").strip()
        
        return generated
    
    except Exception as e:
        print(f"⚠️ Generation error: {e}")
        return f"[Error generating content: {str(e)}]"


def generate_abstract(
    topic: str,
    paper_context: Optional[List[Dict]] = None,
    max_tokens: int = 300
) -> str:
    """
    Generate a formal academic abstract.
    
    Args:
        topic: Main topic/title of the assignment
        paper_context: List of paper dicts with 'title', 'authors', 'year', 'abstract'
        max_tokens: Maximum tokens to generate
    
    Returns:
        Generated abstract text
    """
    context_text = ""
    if paper_context and len(paper_context) > 0:
        context_text = "\n\nResearch papers being analyzed:\n"
        for paper in paper_context[:3]:  # Limit to first 3 papers for context
            context_text += f"- {paper.get('title', 'Unknown')} by {paper.get('authors', 'Unknown')} ({paper.get('year', 'N/A')})\n"
    
    prompt = f"""Write a formal academic abstract on the topic: {topic}.

Instructions:
- Include purpose, methodology, findings, and conclusion
- Make it 150-200 words
- Use technical language appropriate for academic audience
- Structure: Background, Method, Key Findings, Conclusion
{context_text}

Abstract:"""
    
    return generate_text(prompt, max_tokens=max_tokens)


def generate_introduction(
    topic: str,
    paper_context: Optional[List[Dict]] = None,
    max_tokens: int = 400
) -> str:
    """
    Generate an academic introduction section.
    
    Args:
        topic: Main topic of the assignment
        paper_context: List of paper dicts with context information
        max_tokens: Maximum tokens to generate
    
    Returns:
        Generated introduction text
    """
    context_text = ""
    if paper_context and len(paper_context) > 0:
        context_text = "\n\nKey research papers to reference:\n"
        for paper in paper_context[:3]:
            context_text += f"- {paper.get('title', 'Unknown')} ({paper.get('year', 'N/A')})\n"
    
    prompt = f"""Write an academic introduction for an assignment on the topic: {topic}.

Instructions:
- Include background information and importance
- Discuss current research trends and gaps
- Make it 300-400 words
- Start broad and narrow to the specific topic
- Include research questions or objectives
{context_text}

Introduction:"""
    
    return generate_text(prompt, max_tokens=max_tokens)


def generate_discussion(
    topic: str,
    findings: Optional[str] = None,
    paper_context: Optional[List[Dict]] = None,
    max_tokens: int = 500
) -> str:
    """
    Generate a discussion section for an academic assignment.
    
    Args:
        topic: Main topic
        findings: Summary of findings from literature review
        paper_context: Papers being discussed
        max_tokens: Maximum tokens to generate
    
    Returns:
        Generated discussion text
    """
    context_text = ""
    if paper_context and len(paper_context) > 0:
        context_text = "\n\nPapers being discussed:\n"
        for paper in paper_context[:3]:
            context_text += f"- {paper.get('title', 'Unknown')}: {paper.get('abstract', '')[:100]}...\n"
    
    findings_text = f"\n\nKey findings to discuss:\n{findings}" if findings else ""
    
    prompt = f"""Write a discussion section for an academic assignment on {topic}.

Instructions:
- Discuss implications of research findings
- Address challenges and limitations
- Compare and contrast different papers' approaches
- Discuss practical applications
- Make it 600-800 words
- Use critical analysis, not just description
{findings_text}{context_text}

Discussion:"""
    
    return generate_text(prompt, max_tokens=max_tokens)


def generate_conclusion(
    topic: str,
    key_points: Optional[str] = None,
    paper_context: Optional[List[Dict]] = None,
    max_tokens: int = 400
) -> str:
    """
    Generate a formal academic conclusion section.
    
    Args:
        topic: Main topic
        key_points: Main points to summarize
        paper_context: Research papers being concluded on
        max_tokens: Maximum tokens to generate
    
    Returns:
        Generated conclusion text
    """
    context_text = ""
    if paper_context and len(paper_context) > 0:
        context_text = f"\n\nThis analysis reviewed {len(paper_context)} research papers on {topic}."
    
    points_text = f"\n\nKey points to summarize:\n{key_points}" if key_points else ""
    
    prompt = f"""Write a formal academic conclusion for an assignment on the topic {topic}.

Instructions:
- Summarize main findings and contributions
- Discuss theoretical and practical implications
- Suggest future research directions
- Address limitations of current research
- Make it 300-400 words
- End with forward-looking statement
{points_text}{context_text}

Conclusion:"""
    
    return generate_text(prompt, max_tokens=max_tokens)


def generate_with_context(
    section_type: str,
    topic: str,
    papers: List[Dict],
    **kwargs
) -> str:
    """
    Generate any section type with full paper context.
    
    Convenience function that passes all paper metadata as context
    to generate more research-based content.
    
    Args:
        section_type: "abstract", "introduction", "discussion", or "conclusion"
        topic: Main topic
        papers: Full list of Paper objects/dicts
        **kwargs: Additional arguments specific to section type
    
    Returns:
        Generated section text
    """
    paper_context = [
        {
            "id": p.get("id") if isinstance(p, dict) else p.id,
            "title": p.get("title") if isinstance(p, dict) else p.title,
            "authors": p.get("authors") if isinstance(p, dict) else p.authors,
            "year": p.get("year") if isinstance(p, dict) else p.year,
            "abstract": p.get("abstract") if isinstance(p, dict) else p.abstract,
        }
        for p in papers
    ]
    
    if section_type.lower() == "abstract":
        return generate_abstract(topic, paper_context, **kwargs)
    elif section_type.lower() == "introduction":
        return generate_introduction(topic, paper_context, **kwargs)
    elif section_type.lower() == "discussion":
        return generate_discussion(topic, paper_context=paper_context, **kwargs)
    elif section_type.lower() == "conclusion":
        return generate_conclusion(topic, paper_context=paper_context, **kwargs)
    else:
        raise ValueError(f"Unknown section type: {section_type}")


# Module initialization message
print("✨ AI Generator module loaded. Models will load on first use.")
